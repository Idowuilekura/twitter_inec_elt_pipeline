import os
os.system('pip install -q tweepy')
import pandas as pd
import time
from tweepy import Cursor
import tweepy
import argparse
import datetime as dt
from google.cloud import storage
import datetime as dt
until_date_formatted = dt.datetime.now().date().strftime("%Y-%m-%d")
from auth_keys import api

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'./service_account.json'

# def get_use_module():
#     client = storage.Client('idowupluralproj')
#     bucket = client.get_bucket('dtc_data_lake_idowupluralproj')
#     blob = bucket.blob('twitter_folder_tweepy/auth_keys.py')
#     blob.download_to_filename('auth_keys.py')

# get_use_module()

# parser = argparse.ArgumentParser()

# parser.add_argument('--year',help='the year for scrapping the tweet')
# parser.add_argument('--month',help='the month for scapping the tweet')
# parser.add_argument('--day',help='the day to scrap the tweet')

# args = parser.parse_args()

# TWEEPY_FIRST_CREDENTIAL=os.environ['TWEEPY_FIRST_CREDENTIAL']
# TWEEPY_SECOND_CREDENTIAL= os.environ['TWEEPY_SECOND_CREDENTIAL']
# TWEEPY_THIRD_CREDENTIAL=os.environ['TWEEPY_THIRD_CREDENTIAL']
# TWEEPY_FOURTH_CREDENTIAL=os.environ['TWEEPY_FOURTH_CREDENTIAL']

# auth = tweepy.OAuthHandler(TWEEPY_FIRST_CREDENTIAL,TWEEPY_SECOND_CREDENTIAL)
# auth.set_access_token(TWEEPY_THIRD_CREDENTIAL,TWEEPY_FOURTH_CREDENTIAL)
# api = tweepy.API(auth,wait_on_rate_limit=True)


# tweet_scrape_year = int(args.year)
# tweet_scrape_month = int(args.month)
# tweet_scrape_day = int(args.day)


def scrape_tweet_until_date(until_date_formatted: str):
    tweets_list1 = []
    i = 0
    for tweet in tweepy.Cursor(api.search_tweets,q="inec -filter:retweets -filter:replies -filter:hashtags",
                            lang='en',include_entities=True).items(30000):
        tweets_list1.append([tweet.created_at, tweet.text, tweet.user.screen_name,tweet.user.verified,tweet.user.followers_count, tweet.user.friends_count, tweet.retweet_count, tweet.favorite_count])

    tweets_df = pd.DataFrame(tweets_list1, columns=['datetime', 
                                                        'twitter_text', 'username','user_is_verified', 'number_of_followers', 
                                                        'number_of_following','number_of_retweet_count',
                                                        'number_of_tweet_like'])
    return tweets_df

tweets_df = scrape_tweet_until_date(until_date_formatted=until_date_formatted)
# print(tweets_df)
# os.remove('auth_keys.py')

# client = storage.Client()
# bucket = client.get_bucket('dtc_data_lake_idowupluralproj')

