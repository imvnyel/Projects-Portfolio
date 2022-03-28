import tweepy
from credentials import BEARER_TOKEN, MONGO_PWD
import logging
import regex as re
import pymongo

container_name = 'tweet_db'
#container_name = 'localhost'
PORT = 27017

#conn_string = f"mongodb://{container_name}:{PORT}"
conn_string_atlas = f'mongodb+srv://eman_kaunda:{MONGO_PWD}@cluster0.hvvxj.mongodb.net/tweet_database?retryWrites=true&w=majority' #connect to MONGO atlas cloud database
#db_client = pymongo.MongoClient(conn_string)
db_client = pymongo.MongoClient(conn_string_atlas)
db = db_client.twitter


try:
    # The hello command is cheap and does not require auth.
    db_client.admin.command('hello')
    logging.critical('\n########################################\n\
Connection to Mongodb Server Established\
\n########################################\n')
except:
    logging.critical('\n###################################\nConnection to Mongodb Server Failed\n###################################\n')

tweet_files_list = []

client = tweepy.Client(bearer_token=BEARER_TOKEN)

if client:
    logging.critical("\nAuthentication OK")
else:
    logging.critical('\nVerify your credentials')


def main(search_type):    

    if search_type == '1':
        #subject = input('What do you want to find? ')
        
        subject_list = ['tesla', 'the future', 'music industry']
        for i in subject_list:
            print(f'Searching for {i}...')
            cursor = search_tweet(i)
            output_filename = create_txt(cursor, i)
            print(f'Writing results to {output_filename}')
        
        return output_filename
    if search_type == '2':
        subject = input('Enter profile name: ')
        print(f'Searching for {subject}...')
        cursor = profile_search(subject)
        output_filename = create_txt(cursor, subject)
        print(f'Writing results to {output_filename}')
        
        return output_filename

    if search_type == '3':
        quit()

def profile_search(profile):
    
    try:
        user_profile = client.get_user(username=profile,user_fields=['name','id','created_at'])
        user = user_profile.data
        print(user)

        cursor = tweepy.Paginator(
            method=client.get_users_tweets,
            id=user.id,
            exclude=['replies', 'retweets'],
            tweet_fields=['author_id', 'created_at', 'public_metrics']
        ).flatten(limit=20)

        return cursor
    except Exception as e:
        print('There was an error proccessing your request')
        print(e)

def search_tweet(subject):

    search_query = f"{subject} -is:retweet -is:reply -is:quote lang:en -has:links"

    cursor = tweepy.Paginator(
        method=client.search_recent_tweets,
        query=search_query,
        tweet_fields=['author_id', 'created_at', 'public_metrics'],
    ).flatten(limit=100)
    
    return cursor

def clean_tweets(tweet):    
    pattern = re.compile('([.\w]+)')
    tweets_list = re.findall(pattern, tweet)
    return ' '.join(tweets_list)

def create_txt(cursor, subject):
    
    subject_savename = subject.replace(' ','_')
    filename_raw = f'{subject_savename}_tweets_raw.txt'
    filename_cleaned = f'{subject_savename}_tweets_cleaned.txt' 
    i=1
    for tweet in cursor:
            print(f'Writing tweets: {i+1}', end='\r')
            #print(tweet.text+'\n')
            
            raw_tweet = tweet.text
            clean_tweet = clean_tweets(tweet.text)
            
            file_raw = open(filename_raw ,mode='a', encoding='utf-8')
            #file_raw.write('\n\n'+tweet.text)
            db.raw_tweets.insert_one({'tweet_hash': subject, 'tweet': raw_tweet, 'created_at': tweet.created_at})
            
            file_cleaned = open(filename_cleaned ,mode='a', encoding='utf-8')
            #file_cleaned.write('\n\n'+clean_tweet)
            db.tweets.insert_one({'tweet_hash': subject, 'tweet': clean_tweet, 'created_at': tweet.created_at})       

            file_raw.close()
            file_cleaned.close()
            
    return [filename_raw, filename_cleaned] 


##########################RUN PROGRAM##########################
#print('What kind of search would you like to perform?\n1. General Search\n2. Profile Search\n3. Quit')
#search_type = input()

output = main('1')
tweet_files_list.append(output)
