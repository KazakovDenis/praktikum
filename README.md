# Praktikum
  
## Installation
```shell script
pip install -r requirements/production.txt
```
  
## Run application
```shell script
python -m search_service.manage runserver -h <ip> -p <port>
``` 

## Testing  
Install dependencies before
```shell script
pip install -r requirements/test.txt
```
Then execute to run tests
```shell script
python -m pytest -v
```