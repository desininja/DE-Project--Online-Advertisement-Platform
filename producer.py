from confluent_kafka import Producer
import json
from datetime import datetime

# --- Configuration ---
# Ensure this matches your docker-compose.yml advertised listener
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

# --- Message Data ---
# All datetime objects must be converted to ISO 8601 strings
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
    'campaign_start_time': datetime(2025, 9, 1, 12, 0).isoformat(),
    'campaign_end_time': datetime(2025, 9, 2, 14, 0).isoformat(),
    'expenditure_amount': 0.05849999934434891,
    'user_action': 'acquisition',
    'timestamp': datetime.now().isoformat(),
    'click': 0,
    'view': 0,
    'acquisition': 1
}

# --- Produce Message ---

message_json = json.dumps(served_ad)
producer.produce(
        KAFKA_TOPIC,
        message_json.encode('utf-8'),
        callback=delivery_report
    )
producer.flush()  # Wait for all messages to be delivered

# except Exception as e:
#     print(f"Error producing message: {e}")

# finally:
#     # Ensure the producer is closed
#     producer.flush()
#     print("Producer finished.")
