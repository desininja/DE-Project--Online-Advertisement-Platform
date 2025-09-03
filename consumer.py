from confluent_kafka import Consumer, KafkaException
import json
import sys

# --- Configuration ---
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "test-for-online-ads"

# --- Consumer Configuration ---
conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'my_test_consumer_group',
    'auto.offset.reset': 'earliest' # Start consuming from the beginning
}

consumer = Consumer(conf)

def consume_messages():
    """Consumes messages from the Kafka topic."""
    try:
        consumer.subscribe([KAFKA_TOPIC])
        print(f"Listening for messages on '{KAFKA_TOPIC}'...")

        while True:
            # Poll for a message with a timeout of 1 second
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    # End of partition, no more messages for now
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                else:
                    raise KafkaException(msg.error())
            else:
                # Message received successfully
                print("\n--- Message Received ---")
                message_value = msg.value().decode('utf-8')
                try:
                    data = json.loads(message_value)
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    print(f"Message is not valid JSON: {message_value}")
                
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    
    finally:
        consumer.close()

if __name__ == '__main__':
    consume_messages()
