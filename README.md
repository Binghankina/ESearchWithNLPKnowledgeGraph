# ES_NLP_KG
A project improving the elastic search indexing accuracy with NLP generated knowledge graph. The project uses equity research report that collected from internet, and processed the words of report with Tensorflow CNN neural network. The neural network generates a knowledge graph as a dictionary to reveal the relation of words. By utilizing the knowledge graph, we can build elastic search index with words extension to improve the search experience of equity research reports. For example, if the user searches APPL, Google and Facebook related equity research report will also appear in the search result.   

## Dependencies
- python packages
```bash
    $ python3.4 -m venv ../env3
    $ source ../env3/bin/activate
    $ pip3 install -r ./requirements.txt
```
- if docker is not installed
```bash
    // ubuntu
    $ sudo apt-get install docker-ce
    // docker compose
    $ pip3 install docker-compose
```
- postgreSQL
```bash
    $ pkill postgres
    $ docker-compose up -d
    // Connect psql
    $ docker exec -ti <NAME_OF_CONTAINER> psql -U <YOUR_POSTGRES_USERNAME>
    // create DB
    postgres=# CREATE DATABASE touyantong;
```

## Deployment
```bash
    $ python3 manage.py migrate
    $ python3 manage.py runserver <ip>:8000
```

## Authentication

```
(env) ~/Projects/touyantong$ curl http://localhost:8000/api/example
{"detail":"Authentication credentials were not provided."}


(env) ~/Projects/touyantong$ curl -H 'Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImRhb3l1YW5saSIsImV4cCI6MTUwNTU5OTAzNSwiZW1haWwiOiIifQ.bfo67urH-hnMCwFbqXc_51kiy-CxPGASIu5XT2c36To' http://localhost:8000/api/example
{"detail":"Signature has expired."}


(env) ~/curl -X POST -d 'username=daoyuanli&password=mypassword' http://localhost:8000/api/token-auth
{"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImRhb3l1YW5saSIsImV4cCI6MTUwNTYwMDQ3NSwiZW1haWwiOiIifQ.Tu0V70M2bmh9bJ-btU3dBC-5Hq79O-Iwt5MqRcb3dhg"}


(env) ~/Projects/touyantong$ curl -H 'Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImRhb3l1YW5saSIsImV4cCI6MTUwNTYwMDQ3NSwiZW1haWwiOiIifQ.Tu0V70M2bmh9bJ-btU3dBC-5Hq79O-Iwt5MqRcb3dhg' http://localhost:8000/api/example
{"code":0,"results":[{"a":0,"b":1},{"a":1,"b":0}]}
```
