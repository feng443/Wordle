# WordleStat Project

## Setup 

### Environment file

Normally .env should not be checked in, but since this is an example and there is no security concern it is been checked-in.

Run following command

```
docker-compose build
docker-compose up -d
```

this  will start posgres container and also Python container to load data.

To run query, connect to postgres locally by using credentail from .env file. You will need local postgre client.

```
psql --host localhost --username postgres -W
\i modal_score_distribution.sql 
```

Note: I have some trouble with Docker on mac so I end of running the loading data locally:

```
pip3 install -r requirements.txt
./load_wordle_tweets.py
```
