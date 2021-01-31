# Using python 2.7.16
# ./requirements.txt is inside the zip folder

$ pip install -r requirements.txt

$ docker-compose -f docker-compose.yml up -d


# Wait for few minutes

# Open KIBANA
# http://localhost:5601/app/kibana#/dev_tools/console?_g=()

# Add the following schema in KIBANA
#   PUT /test08
#   {
#     "mappings": {
#       "properties": {
#         "LOCATION": {
#           "type": "geo_point"
#         },
#         "DATETIME": {
#           "type": "date"
#         }
#       }
#     }
#   }
#

# Run python producer

$ python pythontweets.py

# Interrupt when you have enough data

------------------------------------------------------
------------------------------------------------------

# There are many ways to test the communication

# Test Kafka messaging tier
1)
$ python consumer.py

2)
$ ./checksql.csh
ksql> PRINT test01 FROM BEGINNING LIMIT 2;

# Test elasticsearch contents
$ ./checkelastic.csh

# Check SCHEMA
$ ./checkmapping.csh
