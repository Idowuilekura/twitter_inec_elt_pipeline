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

since_date = (dt.datetime.now().date() - timedelta(days=20)).strftime("%Y-%m-%d")
end_date = dt.datetime.now().date().strftime("%Y-%m-%d")
def download_twitter_data_scrape(since_date, end_date=True):
    # Creating list to append tweet data 
    tweets_list1 = []
    # Using TwitterSearchScraper to scrape data and append tweets to list
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(f'inec exclude:retweets exclude:replies exclude:hashtags since:{since_date} until:{end_date}').get_items()): #declare a username 
        # if i>10: #number of tweets you want to scrape
        #     # print(tweet.json())
        #     tweets_list1.append([tweet.date, tweet.rawContent, tweet.user.username,tweet.user.verified,tweet.user.followersCount, tweet.user.friendsCount, tweet.replyCount, tweet.retweetCount, tweet.likeCount])
        #     break
        
        tweets_list1.append([tweet.date, tweet.rawContent, tweet.user.username,tweet.user.verified,tweet.user.followersCount, tweet.user.friendsCount, tweet.replyCount, tweet.retweetCount, tweet.likeCount]) #declare the attributes to be returned
        
        

    tweets_df = pd.DataFrame(tweets_list1, columns=['datetime', 
                                                    'twitter_text', 'username','user_is_verified', 'number_of_followers', 
                                                    'number_of_following','number_of_replies','number_of_retweet_count',
                                                    'number_of_tweet_like'])
    
    return tweets_df

