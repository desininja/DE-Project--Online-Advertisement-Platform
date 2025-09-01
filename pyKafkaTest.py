from pykafka import KafkaClient
import json
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()


DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')



try:
    conn = psycopg2.connect(database = DB_NAME,user = DB_USER,password=DB_PASS,host=DB_HOST,port = DB_PORT)
    cursor = conn.cursor()

except (Exception,psycopg2.DatabaseError) as error:
    print(error)

client = KafkaClient(hosts="18.211.252.152:9092")
topic = client.topics['de-capstone1']

consumer =  topic.get_simple_consumer()

for message in consumer:
    if message is not None:
        message_value = message.value.decode('utf-8')
        
        print("Received Messages:")

        print(message_value)
        print("-"*20)
        data = json.loads(message_value)

        print(data)
        print(data['action'])
        # if data['action']=='Stop Campaign':
        #     data_to_insert = (data['text'],data['category'],data['keywords'],data['campaign_id'],'INACTIVE',
        #                       data['target_gender'],data['target_age_range']['start'],data['target_age_range']['end'],
        #                       data['target_city'],data['target_state'],data['target_country'],
        #                       data['target_income_bucket'],data['target_device'],data['cpc'],data['cpa'],
        #                       data['budget'],data['budget'],data['date_range']['start'],
        #                       data['date_range']['end'],data['time_range']['start'],data['time_range']['end'])
        # else:
        #     data_to_insert = (data['text'],data['category'],data['keywords'],data['campaign_id'],'ACTIVE',
        #                       data['target_gender'],data['target_age_range']['start'],data['target_age_range']['end'],
        #                       data['target_city'],data['target_state'],data['target_country'],
        #                       data['target_income_bucket'],data['target_device'],data['cpc'],data['cpa'],
        #                       data['budget'],data['budget'],data['date_range']['start'],
        #                       data['date_range']['end'],data['time_range']['start'],data['time_range']['end'])     
        # print(data_to_insert)

        # sql_query = """
        # INSERT INTO online_ads.ads (text,category,keywords,campaign_id,status,target_gender,target_age_start,
        # target_age_end,target_city,target_state,target_country,target_income_bucket,target_device,cpc,cpa,
        # budget,current_slot_budget,date_range_start,date_range_end,time_range_start,time_range_end)
        # VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        # """
        # cursor.execute(sql_query,data_to_insert)
        # conn.commit()
        # print("Data inserted Successfully!")





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