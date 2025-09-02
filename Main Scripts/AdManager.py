from pykafka import KafkaClient, common
import json
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

try:
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')

except Exception as e:
    print("Error while accessing the environment variables ")
    raise e


try:
    conn = psycopg2.connect(database = DB_NAME,user = DB_USER,password=DB_PASS,host=DB_HOST,port = DB_PORT)
    cursor = conn.cursor()

except (Exception,psycopg2.DatabaseError) as error:
    print(error)

client = KafkaClient(hosts="18.211.252.152:9092")
topic = client.topics['de-capstone1']

consumer =  topic.get_simple_consumer(
    consumer_group=b'ad-manager',
    auto_commit_enable=True,
    reset_offset_on_start=True,
    auto_offset_reset=common.OffsetType.LATEST
)

for message in consumer:
    if message is not None:
        message_value = message.value.decode('utf-8')
        data = json.loads(message_value)

        if data['action']=='Stop Campaign':
            data['status']= 'Inactive'
        else:
            data['status']= 'Active'
        
        data['cpm'] = float(0.0075*float(data['cpc'])) + (0.0005*float(data['cpa']))


        start_date = str(data['date_range']['start'])+" "+str(data['time_range']['start'])
        end_date = str(data['date_range']['end'])+" "+str(data['time_range']['end'])
        start_date = datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S')
        date_dif = end_date-start_date
        num_of_slots = int(date_dif.total_seconds()/60)/10
        data['current_slot_budget'] = round(data['budget']/num_of_slots,2)   
        
        data_to_insert = {'text': data['text'],
                          'category': data['category'], 
                          'keywords': data['keywords'],
                          'campaign_id': data['campaign_id'], 
                          'status': data['status'],
                          'cpm': data['cpm'], 
                          'current_slot_budget': data['current_slot_budget'],
                          'target_gender': data['target_gender'],
                          'target_age_start': data['target_age_range']['start'], 
                          'target_age_end': data['target_age_range']['end'],
                            'target_city': data['target_city'], 
                            'target_state': data['target_state'], 
                            'target_country': data['target_country'],
                            'target_income_bucket': data['target_income_bucket'], 
                            'target_device': data['target_device'], 
                            'cpc': data['cpc'],
                            'cpa': data['cpa'], 
                            'budget': data['budget'], 
                            'date_range_start': data['date_range']['start'], 
                            'date_range_end': data['date_range']['end'], 
                            'time_range_start': data['time_range']['start'],
                            'time_range_end': data['time_range']['end']
                        }
        print(data_to_insert)
        print(data_to_insert['status'])
        columns = ', '.join(data_to_insert.keys())
        placeholders = ', '.join(['%s'] * len(data_to_insert))
        values = tuple(data_to_insert.values())

        update_set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in data_to_insert.keys()])


        sql_query = f"""
        INSERT INTO online_ads.ads ({columns})
        VALUES ({placeholders})
        ON CONFLICT (campaign_id)
        DO UPDATE SET {update_set_clause};
        """
        cursor.execute(sql_query,values)
        conn.commit()
        print("Data inserted Successfully!")





conn.close()
# {"text": "LICTOP 0.4mm Drill Bits Stainless Steel for 3D Printer Nozzle Cleaning Pack of 10",
#   "category": "Tools & Hardware", "keywords": "industrial,scientific,manuf,products", 
#   "campaign_id": "d8ae103c-7a42-11f0-b7f6-0e087721c0e9", 
#   "action": "New Campaign", 
#   "target_gender": "All", 
#   "target_age_range": {"start": "25", "end": "35"}, 
#   "target_city": "All", "target_state": "All", "target_country": "India", "target_income_bucket": "L", 
#   "target_device": "Android Mobile", "cpc": "0.00041", "cpa": "0.0021", "budget": 900,
#   "date_range": {"start": "2025-08-16", "end": "2025-08-17"}, "time_range": {"start": "1:00:00", "end": "20:00:00"}}