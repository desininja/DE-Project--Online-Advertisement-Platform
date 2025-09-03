from typing import Union
from fastapi import FastAPI, Query, HTTPException
import os
from dotenv import load_dotenv
import asyncpg
import uuid
from datetime import datetime
from pydantic import BaseModel
from confluent_kafka import Producer
import json

KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "test-for-online-ads"

# --- Producer Configuration ---
conf = {'bootstrap.servers': KAFKA_BROKER}
producer = Producer(conf)

def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to topic '{msg.topic().encode('utf-8')}'"
              f" [{msg.partition()}] at offset {msg.offset()}")

load_dotenv()

app = FastAPI(title="AD Server and Feedback Handler")

class Action(BaseModel):
    View:int
    Click:int
    Acquisition:int




# Database connection pool - a central object to manage connections.
db_pool = None


@app.on_event("startup")
async def startup_db_pool():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
    except Exception as e:
        print("Error creating database connection pool:")
        print(e)
        raise e
        
@app.on_event("shutdown")
async def shutdown_db_pool():
    if db_pool:
        await db_pool.close()

async def update_budget_async(campaign_id, expenditure_amount):
    """
    Asynchronously updates the budget for a given campaign.
    """
    check_query = """
        SELECT CASE WHEN current_slot_budget - $1 <= 0 OR budget - $1 <= 0 THEN True ELSE False END
        FROM online_ads.ads
        WHERE campaign_id = $2;
        """
    
    async with db_pool.acquire() as conn:
        result = await conn.fetchval(check_query, expenditure_amount, campaign_id)
    print("Check query result:", result)
    if result:
        update_query = """
            UPDATE online_ads.ads
            SET status = 'Inactive', current_slot_budget = current_slot_budget - $1,budget = budget - $1
            WHERE campaign_id = $2;
            """
    else:
        update_query = """
            UPDATE online_ads.ads
            SET current_slot_budget = current_slot_budget - $1,budget = budget - $1
            WHERE campaign_id = $2;
            """
    async with db_pool.acquire() as conn:
        await conn.execute(update_query, expenditure_amount, campaign_id)

    return "Success"


async def get_available_ads_async(device_type, city, state):
    """
    Asynchronously queries the database for the top 2 eligible ads.
    """
    sql_query = """
        SELECT * FROM online_ads.ads
        WHERE status = 'Active' 
        AND target_city IN ($1)
        AND target_state IN ($2)
        AND target_device IN ($3)
        ORDER by cpm DESC
        LIMIT 2;
    """
    async with db_pool.acquire() as conn:
        records = await conn.fetch(sql_query, city, state, device_type)
    return records

async def get_served_ad_async(request_id):
    query = """
            SELECT 
                    campaign_id,
                    user_id,
                    request_id,
                    auction_cpm,
                    auction_cpa,
                    auction_cpc,
                    target_age_range,
                    target_location,
                    target_gender,
                    target_income_bucket,
                    target_device_type,
                    campaign_start_time,
                    campaign_end_time 
            FROM online_ads.served_ads
            WHERE request_id = $1;
            """
    
    async with db_pool.acquire() as conn:
        record = await conn.fetchrow(query, request_id)
    return dict(record)


async def run_auction_served_ad_async(available_ads):
    """
    Asynchronously runs the second-price auction logic.
    """
    if not available_ads:
        return None, None
    
    winning_ad = available_ads[0]
    
    if len(available_ads) == 1:
        auction_cpm = winning_ad['cpm']
        
    else:
        auction_cpm = available_ads[1]['cpm']
    
    # Create the served_ad dictionary from the winning ad and auction details
    served_ad = {
        'request_id': "", # To be filled by the endpoint
        'text': winning_ad['text'],
        'campaign_id': winning_ad['campaign_id'],
        'user_id': "", # To be filled by the endpoint
        'auction_cpm': auction_cpm,
        'auction_cpc': winning_ad['cpc'],
        'auction_cpa': winning_ad['cpa'],
        'target_age_range': f"{winning_ad['target_age_start']} - {winning_ad['target_age_end']}",
        'target_location': f"{winning_ad['target_city']}, {winning_ad['target_state']}, {winning_ad['target_country']}",
        'target_gender': winning_ad['target_gender'],
        'target_income_bucket': winning_ad['target_income_bucket'],
        'target_device_type': winning_ad['target_device'],
        'campaign_start_time': datetime.strptime(f"{winning_ad['date_range_start']} {winning_ad['time_range_start']}",'%Y-%m-%d %H:%M:%S'),
        'campaign_end_time': datetime.strptime(f"{winning_ad['date_range_end']} {winning_ad['time_range_end']}",'%Y-%m-%d %H:%M:%S'),
        'ad_served_timestamp': datetime.now().replace(microsecond=0)
    }
    
    return served_ad

async def write_served_ad_async(served_ad):
    """
    Asynchronously writes the served ad record to the database.
    """
    write_query = """INSERT INTO online_ads.served_ads
                (request_id, text, campaign_id, user_id, auction_cpm, auction_cpc, auction_cpa,
                target_age_range, target_location, target_gender, target_income_bucket,
                target_device_type, campaign_start_time, campaign_end_time, ad_served_timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15);"""
    
    # Convert `served_ad` dictionary values to a list in the correct order for the query
    values = [
        served_ad['request_id'], served_ad['text'], served_ad['campaign_id'], served_ad['user_id'],
        served_ad['auction_cpm'], served_ad['auction_cpc'], served_ad['auction_cpa'],
        served_ad['target_age_range'], served_ad['target_location'], served_ad['target_gender'],
        served_ad['target_income_bucket'], served_ad['target_device_type'],
        served_ad['campaign_start_time'], served_ad['campaign_end_time'],
        served_ad['ad_served_timestamp']
    ]

    try:
        async with db_pool.acquire() as conn:
            await conn.execute(write_query, *values)
    except Exception as e:
        print(f"Error writing to served_ads table: {e}")
        # Note: asyncpg manages transactions implicitly for simple execute calls.

@app.get("/")
def read_root():
    return {"Hello": "World!!"}

@app.get("/ad/user/{user_id}/serve")
async def serve_ads(user_id:str, device_type: str, city: str, state:str):
    available_ads = await get_available_ads_async(device_type, city, state)
    
    if not available_ads:
        raise HTTPException(status_code=404, detail="No eligible ads found.")
    
    served_ad = await run_auction_served_ad_async(available_ads)
    served_ad['user_id'] = user_id
    served_ad['request_id'] = str(uuid.uuid4())
    
    await write_served_ad_async(served_ad)
    
    return {
        "text": served_ad['text'],
        "request_id": served_ad['request_id']
    }

@app.post("/ad/{ad_request_id}/feedback")
async def ad_feedback(ad_request_id: str,action: Action):
    
    user_feedback_time = datetime.now().replace(microsecond=0)
    click = action.Click
    view = action.View
    acquisition = action.Acquisition

    served_ad = await get_served_ad_async(ad_request_id)
    
    
    if not served_ad:
        raise HTTPException(status_code=404, detail="Ad not found.")
    
    if action.Acquisition ==1:
        served_ad['expenditure_amount'] = float(served_ad['auction_cpa'])
        served_ad['user_action'] = 'acquisition'
    elif action.Click ==1:
        served_ad['expenditure_amount'] = float(served_ad['auction_cpc'])
        served_ad['user_action'] = 'click'
    elif action.View ==1:
        served_ad['expenditure_amount'] = 0
        served_ad['user_action'] = 'view'
    await update_budget_async(served_ad['campaign_id'], served_ad['expenditure_amount'])
    served_ad['timestamp'] = user_feedback_time.isoformat()

    served_ad['click'] = click
    served_ad['view'] = view
    served_ad['acquisition'] = acquisition
    served_ad['campaign_start_time'] = served_ad['campaign_start_time'].isoformat()
    served_ad['campaign_end_time'] = served_ad['campaign_end_time'].isoformat()
    print(served_ad)
    print(type(served_ad))
    
    message_json = json.dumps(served_ad)
    producer.produce(
            KAFKA_TOPIC,
            message_json.encode('utf-8'),
            callback=delivery_report
        )
    producer.flush()
    
    return {"status": "Success"}