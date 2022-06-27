#!/usr/bin/env python3

from os import environ as env
import requests
from dotenv import load_dotenv
import tweepy
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import re

id_re = re.compile(r'\#Wordle\s*(\d+)\s*(\d{4}-\d{2}-\d{2})')
dist_re = re.compile(r'([123456X]):[^0-9]*(\d+)')

load_dotenv()

pguser = env['POSTGRES_USER']
pgpass = env['POSTGRES_PASSWORD']
pghost = env['POSTGRES_HOST']
pghost = 'localhost'
db_url = f'postgresql://{pguser}:{pgpass}@{pghost}'

def get_tweets():
    auth = tweepy.OAuth1UserHandler(
        env['TWITTER_CONSUMER_KEY'],
        env['TWITTER_CONSUMER_SECRET'],
        env['TWITTER_ACCESS_TOKEN'],
        env['TWITTER_TOKEN_SECRET']
    )
    api = tweepy.API(auth)

    tweets = api.user_timeline(
        screen_name='WordleStats',
        count=200,
        tweet_mode='extended'
    )

    # parse out tweets
    # This is assuming all tweet will be same format. 
    # Should add exception handling in read code
    df = pd.DataFrame()
    for t in tweets:
        d = [0] * 7
        for l in t.full_text.split('\n'):
            m = id_re.match(l)
            if m: 
                puzzle_number, dt = m.groups() 
            else:
                m = dist_re.match(l)
                if m:
                    tries, perc = m.groups()
                    if tries == 'X':  # Treated the X as number 7, which is index at 6
                        d[6] = perc
                    else:
                        d[int(tries) - 1] = int(perc)
        df = df.append(dict(
            puzzle_number=int(puzzle_number), dt=dt,
            distribution=d), ignore_index=True)

    return df

def get_answers():
    '''
    Return: dictionay of answers by date
    '''
    url = 'https://paste.ee/d/4zigF/0'
    r = requests.get(url)

    """
    Assume format below
    <U+FEFF>Date    Wordle #        Word
    6/19/2021       0       cigar
    """
    
    lookup = {}
    for l in r.iter_lines():
        date, id, word = l.decode('UTF-8').split('\t')
        try: # Simplified
            (month, day, year) = date.split('/')
            lookup['{:4d}-{:02d}-{:02d}'.format(int(year), int(month), int(day))] = word
        except:
            print(f'not a date: {date}')

    return lookup
    
def write_tweets_with_answers(tweets, answers):
    tweets['word'] = tweets['dt'].apply(lambda x: answers[x])

    conn = create_engine(db_url).connect()
    tweets.to_sql('wordle_records', con=conn, if_exists='replace')
    print('Done')

if __name__ == "__main__":
    tweets = get_tweets()
    answers = get_answers()
    write_tweets_with_answers(tweets, answers)

