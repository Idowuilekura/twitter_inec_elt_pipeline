import os
# from prettyprint import prettyprint
import pprint
os.system('pip install snscrape')
try:
    import snscrape.modules.twitter as sntwitter
    print('imported snscrape')
except:
    print('no module found')
import pandas as pd
import datetime as dt
from datetime import timedelta
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('--year',help='the year for scrapping the tweet')
parser.add_argument('--month',help='the month for scapping the tweet')
parser.add_argument('--day',help='the day to scrap the tweet')

args = parser.parse_args()

tweet_scrape_year = int(args.year)
tweet_scrape_month = int(args.month)
tweet_scrape_day = int(args.day)

# since_date = (dt.datetime.now().date() - timedelta(days=20)).strftime("%Y-%m-%d")
# end_date = dt.datetime.now().date().strftime("%Y-%m-%d")

try:
    since_date = dt.datetime(tweet_scrape_year,tweet_scrape_month,tweet_scrape_day)
    since_date_formatted = since_date.date().strftime("%Y-%m-%d")
    end_date = ( since_date + timedelta(days=1)).strftime("%Y-%m-%d")
except:
    pass

def download_twitter_data_scrape(since_date, end_date, scrape_all=True):
    print(f"scrapping for {since_date} to {end_date}")
    # Creating list to append tweet data 
    tweets_list1 = []
    # Using TwitterSearchScraper to scrape data and append tweets to list
    if scrape_all:
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(f'inec exclude:retweets exclude:replies exclude:hashtags since:{since_date} until:{end_date}').get_items()): #declare a username 
            # if i>10: #number of tweets you want to scrape
            #     # print(tweet.json())
            #     tweets_list1.append([tweet.date, tweet.rawContent, tweet.user.username,tweet.user.verified,tweet.user.followersCount, tweet.user.friendsCount, tweet.replyCount, tweet.retweetCount, tweet.likeCount])
            #     break
            tweets_list1.append([tweet.date, tweet.rawContent, tweet.user.username,tweet.user.verified,tweet.user.followersCount, tweet.user.friendsCount, tweet.replyCount, tweet.retweetCount, tweet.likeCount]) #declare the attributes to be returned
    else:
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(f'inec exclude:retweets exclude:replies exclude:hashtags since:{since_date} until:{end_date}').get_items()): #declare a username 
            if i>10: #number of tweets you want to scrape
                # print(tweet.json())
                tweets_list1.append([tweet.date, tweet.rawContent, tweet.user.username,tweet.user.verified,tweet.user.followersCount, tweet.user.friendsCount, tweet.replyCount, tweet.retweetCount, tweet.likeCount])
                break


    tweets_df = pd.DataFrame(tweets_list1, columns=['datetime', 
                                                    'twitter_text', 'username','user_is_verified', 'number_of_followers', 
                                                    'number_of_following','number_of_replies','number_of_retweet_count',
                                                    'number_of_tweet_like'])
    
    return tweets_df

tweets_df = download_twitter_data_scrape(since_date=since_date_formatted,end_date=end_date, scrape_all=True)
print(tweets_df.tail())
print('done scrapping')


