## Twitter to Kibana real-time data processing pipeline
---
### Overview
This repository builds a data processing pipeline that is useful for doing exploratory data analysis (EDA) on real-time streaming data.

More particularly, the repository visualizes the hotspots of "Covid-19" with sentiments on real-time streaming [Twitter][twitter] tweets.

The aim of this repository is to only show the connections between different systems for accomplishing the visualization of data. The streaming processing pipeline consists of Kafka messaging queue, Elasticsearch and connectors between the two and Kibana. 

### Big Data Source

Twitter data is enormous - around [500 million][volume] tweets per day. Retrieving tweet data even with search filters, viz. 'pandemic' etc., can get us 10-15 tweets per second. 

In order to not drop any of the tweets, a multi-agent system with a load balancer can be devised. However, for this home-kit project, the tweets are dropped whenever Kafka messaging tier is beyond capacity and not able to handle more data. Scalability can be addressed as a future work. 

Storage is not an issue though because tweets contains only 140 characters. Images and other artifacts are dropped from twitter data.

The schema gets **location** and **text** from the tweets. We collect **sentiments** from the tweets and current **datetime** to the schema.

### Processing Pipeline
![Processing Pipeline](https://github.com/sdbma/Twitter2KibanaPipeline/blob/main/images/pipelines.png)

The schema used to process twitter streams and extract data is the following:
```sql
SCHEMA {
    LOCATION: geo_point;
    DATETIME: date;
    SENTIMENT: string;
    TEXT: string;
}
```
The AVRO producer writes the above data to the Kafka messaging queue. The Confluent platform is used to create Kafka to Elasticsearch connector, Elasticsearch and Kibana interfaces.
### Implementation
First step is to get the twitter tweets from streaming twitter API. The callback mechanism with required search string is added to [tweepy][tweepy] interface.
The method **MyStreamListener::on_status()** creates the schema as described earlier. **Location** is obtained from the user's location but also can be obtained through tweet's geo_point, however, most users do not share their GPS location. The **datetime** is the current timestamp. The **sentiment** is obtained through NLP (Natural Language Processing) library [TextBlob][textblob] and is usually among the three values {*positive*,*negative*,*neutral*}. The user location from the tweet is converted to [latitude,longitude] form by using OpenStreetMap Nominatim [API][geopy].
The next layer is [Kafka][kafka] messaging tier. [Avro][avro] producer is used to produce the code. AvroProducer uses the schema registry (http://localhost:8081) to register the schema. It uses bootstrap_servers location (http://localhost:9092) to write the message to Kafka messaging queue. 
The KSQLDB interface (http://localhost:8088) is used to create the following streams. This creates Kafka to [Elasticsearch][elasticsearch] connector. It also registers the stream with the schema. The schema is not ignored and is same as the schema defined in earlier section.
[Kibana][kibana] is used for visualization. Kibana is set in the docker compose file as part of confluent platform.
### HOW TO RUN
Docker image is used for the confluent platform. Relevant versions of python package is required - not every version is compliant.
```sh
# Using python 2.7.16
# ./requirements.txt is inside the zip folder
$ pip install -r requirements.txt
$ docker-compose -f docker-compose.yml up -d
```
The next thing to do is to create a schema in Kibana interface containing the non-basic type fields of schema. For visualizing geographical points in Kibana, we need to specify **LOCATION** as of type **geo_point**. Also, for specifying time as index pattern, we need to specify **DATETIME** as of type **date**. The index creation must be done before we allow AvroProducer to register its schema and dump its data. AvroProducer in the processing pipeline emits schema fields as strings, so unless we specify these fields earlier in Kibana, we would only be seeing strings, and not *geo_point* and *data*. The string geo-points are ordered as *latitude*,*longitude*. 

![KibanaSchema](https://github.com/sdbma/Twitter2KibanaPipeline/blob/main/images/kibana.png)

We can check the mapping of the index using the following command:
```csh
$ ./checkmapping.csh
{
    "test08": {
        "mappings": {
            "properties": {
                "DATETIME": {
                    "type": "date"
                }
                "LOCATION": {
                    "type": "geo_point"
                }
            }
        }
    }
}
```

Along with running producer, we can run the consumer and kafkcat to check the outputs of Kafka messaging queue.
```sh
$ python pythontweets.py
$ python consumer.py
$ docker run -it --network=host edenhill/kafkacat:1.6.0 -b localhost:9092 -t test08 -J
```
We can check the contents of elastic search as well:
```sh
$ ./checkelastic.csh
```
The index mapping now shows all the 4 fields of Schema.
```sh
$ ./checkmapping.csh
{
    "test08": {
        "mappings": {
            "properties": {
                "DATETIME": {
                    "type": "date"
                }
                "LOCATION": {
                    "type": "geo_point"
                }
                "SENTIMENT": {
                    "type"="text"
                }
                "TEXT": {
                    "type":"text"
                }
            }
        }
    }
}
```
Going back to Kibana interface, we can get the following output that shows data along with SCHEMA.
![KibanaResults](https://github.com/sdbma/Twitter2KibanaPipeline/blob/main/images/kibana2.png)

Next, created index patterns, that looks like the following:
![KibanaIndex](https://github.com/sdbma/Twitter2KibanaPipeline/blob/main/images/kibana3.png)

Now, it's time visualize the results in the dashboard.
![KibanaVisuals](https://github.com/sdbma/Twitter2KibanaPipeline/blob/main/images/kibana4.png)

We can filter by sentiments and datetime in the above visualization.

The heat map can also be seen as below:
![KibanaHeatMap](https://github.com/sdbma/Twitter2KibanaPipeline/blob/main/images/kibana5.png)

### Limitations
* Streaming twitter API - some tweets being dropped
  * Scalbility issue - need to add more Kafka connections
  * Processing before messaging tier consumes time
  * Geocoder API times out due to Nomination usage policy
* Real-time system does not handle historical data

### Conclusion
* Demonstrated real-time data processing pipeline from streaming twitter visualization using Kafka and ElasticSearch tiers.
* Possible extension of the project
  * Scalability improvement using Apache Flink processing layer after Kafka messaging layer
  * Spark-streaming layer with Hadoop cluster for processing historical data.

Please contact [Shomit Dutta](mailto:shomitdutta@gmail.com) for follow-up questions. 

License
----

MIT License

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [twitter]: <https://twitter.com/home>
   [volume]: <https://www.oberlo.com/blog/twitter-statistics#:~:text=500%20million%20tweets%20are%20sent%20out%20per%20day.,has%20been%20used%20more%20than%20two%20billion%20times.>
   [tweepy]:<https://www.tweepy.org/>
   [textblob]:<https://pypi.org/project/textblob/>
   [geopy]:<https://geopy.readthedocs.io/en/stable/>
   [kafka]:<https://kafka.apache.org/>
   [avro]:<https://avro.apache.org/>
   [elasticsearch]:<https://www.elastic.co/elasticsearch/>
   [kibana]:<https://www.elastic.co/kibana>
