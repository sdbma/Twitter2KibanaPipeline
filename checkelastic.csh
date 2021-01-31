curl -s http://localhost:9200/test08/_search -H 'content-type: application/json' -d '{ "size": 42  }' | jq -c '.hits.hits[]'
