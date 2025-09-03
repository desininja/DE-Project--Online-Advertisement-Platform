from pykafka import KafkaClient
import json 
from datetime import datetime

# Sample served_ad dictionary with datetime objects
served_ad = {
    'campaign_id': 'b1b99ac4-872f-11f0-b7f6-0e087721c0e9',
    'user_id': '123',
    'request_id': 'e9d14495-872a-4b53-87f2-038b5e7bf2bd',
    'auction_cpm': 3.8624999433523044e-05,
    'auction_cpa': 0.05849999934434891,
    'auction_cpc': 0.0012799999676644802,
    'target_age_range': '0 - 0',
    'target_location': 'All, All, India',
    'target_gender': 'All',
    'target_income_bucket': 'All',
    'target_device_type': 'All',
    # Convert datetime objects to ISO 8601 strings
    'campaign_start_time': datetime(2025, 9, 1, 12, 0).isoformat(),
    'campaign_end_time': datetime(2025, 9, 2, 14, 0).isoformat(),
    'expenditure_amount': 0.05849999934434891,
    'user_action': 'acquisition',
    'timestamp': datetime(2025, 9, 4, 1, 38, 14).isoformat(),
    'click': 0,
    'view': 0,
    'acquisition': 1
}

kafka_client = KafkaClient(hosts="127.0.0.1:9092")
kafka_topic = kafka_client.topics['test-for-online-ads']

with kafka_topic.get_sync_producer() as producer:
    # Encode the JSON string to bytes before producing
    producer.produce(json.dumps(served_ad).encode('utf-8'))
    print("Message produced successfully")



/opt/kafka/bin $ ./kafka-console-producer.sh  --topic test-for-online-ads  --bootstrap-server broker:29092