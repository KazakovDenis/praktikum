# Search service
  
## Installation
Clone this repository then install dependencies:
```shell script
pip install -r search_service/requirements/production.txt
```
  
## Run application
Execute:
```shell script
python -m search_service.manage runserver
``` 
and visit [localhost](http://127.0.0.1:8000)

## Testing  
Install dependencies before
```shell script
pip install -r search_service/requirements/test.txt
```
then execute the command below to run tests
```shell script
python -m pytest -v
```