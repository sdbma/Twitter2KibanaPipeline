from kafka import KafkaConsumer
from json import loads
from time import sleep
consumer = KafkaConsumer(
    'test08',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
)
for event in consumer:
    event_data = event.value
    print(event_data)
    sleep(1)
