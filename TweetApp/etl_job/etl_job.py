import pymongo
from sqlalchemy import create_engine
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
import logging
import regex as re
from etl_credentials import PG_PWD, PG_PWD_AWS, MONGO_PWD


#Create MONGO DB connection params
MONGO_HOST = 'tweet_db'
#MONGO_HOST = 'localhost'
MONGO_PORT = 27017

MONGO_CONN = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"
#mongo_client = pymongo.MongoClient(MONGO_CONN)

conn_string_atlas = f'mongodb+srv://eman_kaunda:{MONGO_PWD}@cluster0.hvvxj.mongodb.net/tweet_database?retryWrites=true&w=majority' #connect to MONGO atlas cloud database
#db_client = pymongo.MongoClient(conn_string)
mongo_client = pymongo.MongoClient(conn_string_atlas)

db_twitter = mongo_client.twitter
raw_tweet_collection = db_twitter.raw_tweets

try:
    # The hello command is cheap and does not require auth.
    mongo_client.admin.command('hello')
    logging.critical('\n########################################\n\
Connection to Mongodb Server Established\
\n########################################\n')
except:
    logging.critical('\n###################################\nConnection to Mongodb Server Failed\n###################################\n')



#Create POSTGRES connection params
PG_USER = 'postgres'
#PG_HOST = 'localhost'
#PG_HOST = 'tweets-db.cwltwm28r8mm.eu-central-1.rds.amazonaws.com' --trying to connect to AWS database
PG_HOST = 'tweets_sentiment'
PG_PORT = 5432
pg_db = 'tweets_sentiments'


# Connection string
try:
    PG_CONN = f"postgresql://{PG_USER}:{PG_PWD}@{PG_HOST}:{PG_PORT}" 
    #PG_CONN = f"postgresql://{PG_USER}:{PG_PWD_AWS}@{PG_HOST}:{PG_PORT}" --trying to connect to AWS database
    pg = create_engine(PG_CONN, echo=True)
except:
    print(f'Could not connect to database {pg_db}')
    
    


# Creating a table
pg.execute("""
CREATE TABLE IF NOT EXISTS tweets_table (
    id BIGSERIAL,
    topic TEXT,
    transformed_text TEXT,
    sentiment FLOAT,
    created_at TIMESTAMP
);
""")

print('Table Created')
s  = SentimentIntensityAnalyzer()

def tweet_clean(tweet):
    mentions_pattern = '@[a-zA-Z0-9]+'
    hashtag_pattern = '#'
    
    #print(tweet)
    #print(type(tweet))
    
    tweet = re.sub(mentions_pattern, '', tweet)
    tweet = re.sub(hashtag_pattern, '', tweet)
    
    return tweet

def extract():
    """_summary_
        Extracts tweets from MONGODB 
    Returns:
        _type_: _description_
        list: list of tweet collection
    """
    
    raw_tweet_list = list(raw_tweet_collection.find())
    
    return raw_tweet_list

def transform(tweet):

    
    tweet_text_clean = tweet_clean(tweet)
    sentiment = s.polarity_scores(tweet_text_clean)
    sentiment_score = sentiment['compound']

    logging.critical("\n---TRANSFORMATION COMPLETED---")
    return tweet_text_clean, sentiment_score

def load(topic, tweet, sentiment, timestamp):
    
    if pg.execute(f"""
    INSERT INTO tweets_table (topic, transformed_text, sentiment, created_at) 
    VALUES ('{topic}','{tweet}','{sentiment}','{timestamp}');
    """
        ):
        logging.critical(f"TWEET AND SENTIMENT {sentiment} LOADED INTO POSTGRES")

###########RUN PROGRAM##################
i=0
for tweet_data in extract():
    topic = tweet_data['tweet_hash']
    timestamp = tweet_data['created_at']
    tweet_text = tweet_data['tweet']
    try:
        i+=1
        logging.critical(f"\n---TWEET EXTRACTED---\n{topic}: {i}/{len(extract())}")
        song_transformed, sentiment_score = transform(tweet_text)
        load(topic, song_transformed,sentiment_score, timestamp)
    except Exception as e:
        print("Database load failed")
        print(e)
        pass