# Copyright @2021 Shomit Dutta
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.

from time import sleep
from json import dumps
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from confluent_kafka import Producer
import logging
import ksql
from ksql import KSQLAPI
import ksql.utils as utils
import socket
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from json import dumps
from kafka import KafkaProducer, KafkaClient
from textblob import TextBlob
from geopy.geocoders import Nominatim
from urllib3.exceptions import ProtocolError
from datetime import datetime, timedelta
import re
# encoding=utf8
import sys


consumer_key = "xxxxxxxxxxxDxxxPxxxxxxZCj"
consumer_secret =  "YxxxxxxxxxxxmzAO1rFQzxxxxxxxxiBnKP5dwUxxxxRxx6woQu"
access_token =  "136xxxxx21-yxxxxxxxxxxxxxxxxxxxxxxxxxxXGaMslxxxxBY"
access_token_secret =  "bxxxxxxxxxxxxxxIjKCBtYxxxxxxxxxxxxxxxxxxxxQui"


def clean_tweet(data):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ", data).split())

def get_sentiment(data):
    analysis = TextBlob(clean_tweet(data))
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity == 0:
        return "neutral"
    else:
        return "negative"

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def gettimestamp(dt):
    # timezone.utc not supported in python 2.7
    #return int((dt - datetime(1970,1,1)).total_seconds() /
    #           float(timedelta(milliseconds=1).total_seconds()))
    return dt.utcnow().isoformat()

class MYKSQLAPI():
    def __init__(self):
        url = "http://localhost:8088"
        self.api_client = KSQLAPI(url)
        self.topic = "test08"
        self.bootstrap_servers = "localhost:9092"
        if utils.check_kafka_available(self.bootstrap_servers):
            value_schema_str = """ 
            { 
                "type": "record", 
                "namespace": "com.example", 
                "name": "value", 
                "fields": [ 
                    {"name":"LOCATION", "type":"string"}, 
                    {"name":"DATETIME", "type":"string"}, 
                    {"name":"SENTIMENT", "type":"string"}, 
                    {"name":"TEXT", "type":"string"} 
                ] 
            } 
            """
            key_schema_str = """ 
            { 
                "type": "record", 
                "namespace": "com.example", 
                "name": "key", 
                "fields": [ 
                    {"name":"LOCATION", "type":"string"}, 
                    {"name":"DATETIME", "type":"string"}, 
                    {"name":"SENTIMENT", "type":"string"}, 
                    {"name":"TEXT", "type":"string"} 
                ] 
            } 
            """
            value_schema = avro.loads(value_schema_str)
            key_schema = avro.loads(key_schema_str)
            self.key = {"LOCATION": "LOCATION", "DATETIME":"DATETIME",
                        "SENTIMENT":"SENTIMENT", "TEXT":"TEXT"}
            self.producer = AvroProducer({ 
                    'bootstrap.servers':self.bootstrap_servers, 
                    'on_delivery': delivery_report, 
                    'schema.registry.url': 'http://localhost:8081' 
                }, default_key_schema=None, 
                default_value_schema=value_schema);
        else:
            print("Could not connect to Kafka")
            exit(-1)
            
    def create_stream(self):
        self.api_client.ksql("CREATE STREAM TEST08 (LOCATION STRING, DATETIME STRING, SENTIMENT STRING, TEXT STRING) WITH (KAFKA_TOPIC='test08', PARTITIONS=1, VALUE_FORMAT='JSON');");
        self.api_client.ksql("CREATE SINK CONNECTOR SINK_ELASTIC_TEST_08 WITH ('connector.class' = 'io.confluent.connect.elasticsearch.ElasticsearchSinkConnector','connection.url'  = 'http://elasticsearch:9200','key.converter'   = 'org.apache.kafka.connect.storage.StringConverter','type.name'       = '_doc','topics'          = 'test08','key.ignore'      = 'true','behavior.on.null.values'='delete','schema.ignore'   = 'false');")
        pass

    def produce(self, message):
        self.producer.produce(topic=self.topic, key=None,value=message)

    def flush(self):
        self.producer.flush()

class MyStreamListener(StreamListener):
    def on_status(self, status):
        try:
            app = Nominatim(user_agent="JournalDev")
            location = app.geocode(status.user.location)
            if location:
                location = str(location.latitude) + "," + str(location.longitude)
                text = status.text.encode('utf-8')
                message = { "LOCATION":location, 
                            "DATETIME": gettimestamp(status.created_at),
                            "SENTIMENT": get_sentiment(text), 
                            "TEXT":text[0:127]}
                print (message)
                client.produce(message)
                sleep(1)
        except Exception as e:
            print e.message
        return True
    def on_error(self, status):
        print (status)

reload(sys)
sys.setdefaultencoding('utf8')
client = MYKSQLAPI()
client.create_stream()
l = MyStreamListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)
while True:
    try:
        stream.filter(track=["covid", "corona", "pandemic"])
    except (ProtocolError, AttributeError):
        continue
