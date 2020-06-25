# Search service
  
## Installation
Clone this repository then install dependencies:
```shell script
pip install -r search_service/requirements/production.txt
```
  
## Usage
Execute to run Elasticsearch server from a docker container:
```shell script
docker run --name elastic -d --rm -p 9200:9200 -e "discovery.type=single-node" -v es_data:/usr/share/elasticsearch/data docker.elastic.co/elasticsearch/elasticsearch:7.7.0
``` 

Execute to run the application:
```shell script
python -m search_service.manage runserver
``` 
and visit http://127.0.0.1:8000

## Testing  
Install dependencies before
```shell script
pip install -r search_service/requirements/test.txt
```
then execute the command below to run tests
```shell script
python -m pytest -v
```