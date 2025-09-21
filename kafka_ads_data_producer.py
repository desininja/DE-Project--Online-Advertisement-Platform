import csv
import json
from confluent_kafka import Producer
import time
import random as rand

# Configuration for the Kafka Producer

KAFKA_BROKER = 'localhost:9092'


KAFKA_TOPIC = 'de-project-ads-topic'


CSV_FILE_PATH = 'kafka_ads_output.csv'

def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery status."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to topic {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def produce_messages_from_csv():
    """Reads a CSV file and produces each row as a Kafka message."""
    
    producer_config = {
        'bootstrap.servers': KAFKA_BROKER
    }
    producer = Producer(producer_config)

    try:
        
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as csvfile:
            
            reader = csv.DictReader(csvfile)
            
            # Iterate over each row in the CSV
            for row in reader:
                
                key = str(row.get('campaign_id', json.dumps(row)))  
                
                
                value = json.dumps(row)
                
                
                producer.produce(
                    topic=KAFKA_TOPIC,
                    key=key.encode('utf-8'),
                    value=value.encode('utf-8'),
                    callback=delivery_report
                )
                
                time.sleep(rand.randint(1, 15))
                producer.poll(0)

    except FileNotFoundError:
        print(f"Error: The file '{CSV_FILE_PATH}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        
        print("\nFlushing messages to ensure all are sent...")
        producer.flush()
        print("Done.")

if __name__ == "__main__":
    produce_messages_from_csv()
