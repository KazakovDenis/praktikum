# Full text search service
  
## Installation
Create and activate virtual environment
```shell script
python -m venv venv && source venv/bin/activate
```
Clone this repository and then install dependencies:
```shell script
pip install -r search_service/requirements/production.txt
```

## Preparation
Execute the command below to run Elasticsearch server from a docker container:
```shell script
docker run --name elastic -d --rm -p 9200:9200 -e "discovery.type=single-node" -v es_data:/usr/share/elasticsearch/data docker.elastic.co/elasticsearch/elasticsearch:7.7.0
``` 
Create and fill ES index with db data
```shell script
python -m practice.sprint_1.etl.etl_elastic
```

## Usage
Execute the command below to run the application:
```shell script
python -m search_service.manage runserver
``` 
and visit http://127.0.0.1:8000

## Testing  
Install dependencies before
```shell script
pip install -r search_service/requirements/test.txt
```

### Unit testing
Execute the command below to run unit tests
```shell script
python -m pytest
```

### Coverage
Execute the command below to check test coverage
```shell script
coverage run -m pytest && coverage report -m && coverage html
```
and open `htmlcov/index.html` in a browser

### Load testing
Run the application then execute the command below to run load tests
```shell script
docker run --name vegeta --rm --network host -v /path/to/search_service/tests/load:/vegeta peterevans/vegeta:latest sh -c "vegeta attack -targets /vegeta/targets.txt -timeout 2s -duration 10s -rate 30/1s | vegeta report > /vegeta/result.txt"
```
and check results out in `search_service/tests/load/result.txt`
