import re
import pyspark 
import pandas as pd
from pyspark.sql import types, SparkSession, functions as F
from google.cloud import bigquery
# from download_twitter_data_tweepy import tweets_df
import os
os.system("pip install textblob")
os.system("pip install -U regex")
from textblob import TextBlob
import datetime as dt
from dotenv import load_dotenv

load_dotenv()
# until_date_formatted = dt.datetime.now().date().strftime("%Y-%m-%d")
date_yesterday = (dt.datetime.now().date()- dt.timedelta(1)).strftime("%Y-%m-%d")

def remove_url(tweet):
    # text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    clean_tweet = re.sub(r'https?:\/\/\S*', '', tweet, flags=re.MULTILINE)
    clean_tweet = re.sub("@[A-Za-z0-9_]+","", clean_tweet)
    clean_tweet = re.sub("#[A-Za-z0-9_]+","", clean_tweet)

    return clean_tweet

def get_sentiment_tweet(tweet):
    # tweet_sentiment_pipeline = pipeline("sentiment-analysis")
    # tweet_data = [tweet]
    textblob_text = TextBlob(tweet)
    sentiment_score = textblob_text.sentiment.polarity
    if sentiment_score > 0:
        return 1
    elif sentiment_score < 0:
        return -1
    else:
        return 0

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

def filter_text(text):
    filter_pattern = r'contact\s+(?:us|me)|contact:\s*\d+'
    if re.match(filter_pattern, text):
        return 0
    return 1

# def convert_user_verified(user_text:bool):
#     if user_text == True:
#         return 1
#     return 0

remove_url_udf = F.udf(remove_url)
demojify_udf = F.udf(deEmojify)
get_sentiment_data_udf = F.udf(get_sentiment_tweet)
# convert_user = F.udf(convert_user_verified)
filter_irrelevant_content = F.udf(filter_text)

schema_twitter = types.StructType([
            types.StructField('datetime', types.TimestampType(), True), 
            types.StructField('twitter_text', types.StringType(), True), 
            types.StructField('username', types.StringType(), True), 
            types.StructField('user_is_verified', types.BooleanType(), True), 
            types.StructField('number_of_followers', types.LongType(), True), 
            types.StructField('number_of_following', types.LongType(), True),
            types.StructField('number_of_retweet_count', types.LongType(), True), 
            types.StructField('number_of_tweet_like', types.LongType(), True)
           ])



# bigquery_schema = [
#     bigquery.SchemaField('datetime',"TIMESTAMP",mode="REQUIRED"),
#     bigquery.SchemaField('twitter_text',"STRING",mode="REQUIRED"),
#     bigquery.SchemaField('username',"STRING",mode="REQUIRED"),
#     bigquery.SchemaField('user_is_verified',"BOOL",mode="REQUIRED"),
#     bigquery.SchemaField('number_of_followers',"INTEGER",mode="REQUIRED"),
#     bigquery.SchemaField('number_of_following',"INTEGER",mode="REQUIRED"),
#     bigquery.SchemaField('number_of_replies',"INTEGER",mode="REQUIRED"),
#     bigquery.SchemaField('number_of_retweet_count',"INTEGER",mode="REQUIRED"),
#     bigquery.SchemaField('number_of_tweet_like',"INTEGER",mode="REQUIRED")
# ]


# spark_session = SparkSession.builder.appName('spark_sql').getOrCreate()

# # tweet_spark_df = spark_session.createDataFrame(tweets_df, schema=schema_twitter)

# print(tweet_spark_df.schema)
project_name = os.getenv("PROJECT_NAME")
dataset_name = os.getenv("DATASET_NAME")
table_name = os.getenv("TABLE_NAME")
dataset_id = project_name+'.'+dataset_name
bigquery_table_id = project_name+'.'+dataset_name+'.'+table_name
bigquery_table_id_without_project = dataset_name+'.'+table_name

client = bigquery.Client(project_name)
dataset = client.dataset(dataset_name)
table_ref = dataset.table(table_name)


dataset_location = os.getenv("DATASET_LOCATION")

def create_dataset_if_not_exist(client:str, dataset_id:str,dataset_location:str):
   
    try:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = dataset_location
        client.create_dataset(dataset, timeout=30)
    except:
        pass

create_dataset_if_not_exist(client,dataset_id,dataset_location=dataset_location)

def create_spark_session_and_spark_df(df_path:str):

    spark_session = SparkSession.builder.appName('spark_sql').getOrCreate()

    # tweet_spark_df = spark_session.createDataFrame(tweets_df, schema=schema_twitter)
    tweet_spark_df = spark_session.read.parquet(df_path)

    tweet_spark_df = tweet_spark_df.withColumn('twitter_text', remove_url_udf('twitter_text')) \
            .withColumn('twitter_text', demojify_udf('twitter_text')).withColumn('tweet_sentiment', get_sentiment_data_udf('twitter_text')) 
            # \
            # .withColumn('relevant_tweets', filter_irrelevant_content('twitter_text')) \
            # .filter(F.col('relevant_tweets') == 1).drop("relevant_tweets")

            # .withColumn('user_is_verified', convert_user('user_is_verified')).show()
            # .withColumn('relevant_tweets', filter_irrelevant_content('twitter_text')) \
            # .filter(F.col('relevant_tweets') == 1).drop("relevant_tweets").drop("user_is_verified").show()

    return spark_session, tweet_spark_df

GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
spark_session, tweet_spark_df = create_spark_session_and_spark_df(df_path=GCP_BUCKET_NAME + '/' + f'twitter_data/data_{date_yesterday}.parquet.gzip')
print(tweet_spark_df.show())

bucket = os.getenv("DATAPROC_STAGING_BUCKET")
spark_session.conf.set('temporaryGcsBucket', bucket)

def check_if_table_exist_and_create(client, table_ref,bigquery_table_id_without_project,tweet_spark_df):
    from google.cloud.exceptions import NotFound
    try:
        client.get_table(table_ref)
        print('got the table')
        # tweet_spark_df.write.format('bigquery').option('table', bigquery_table_id).mode('append').save()
        # tweet_spark_df.write.mode('append').format('bigquery').save(bigquery_table_id)

        tweet_spark_df.write.mode('append').format('bigquery').option('table',bigquery_table_id_without_project).save()
    except NotFound:
        tweet_spark_df.write.mode('overwrite').format('bigquery').option('table',bigquery_table_id_without_project).save()
        print('write to table')
        #  table = bigquery.Table(bigquery_table_id, schema=bigquery_schema)
        #  table = client.create_table(table)
        #  tweet_spark_df.write.mode('overwrite').format('bigquery').save(bigquery_table_id)
        #  tweet_spark_df.write.format('bigquery').option('table', bigquery_table_id).mode('overwite').save()

# if check_if_table_exist:
#     tweet_spark_df.write.format('bigquery').option('table', bigquery_table_id).mode('append').save()
# else:
#     table = bigquery.Table(bigquery_table_id, schema=bigquery_schema)
#     table = client.create_table(table)
#     tweet_spark_df.write.format('bigquery').option('table', bigquery_table_id).mode('overwite').save()

# check_if_table_exist_and_create
check_if_table_exist_and_create(client=client,table_ref=table_ref,bigquery_table_id_without_project=bigquery_table_id_without_project,tweet_spark_df=tweet_spark_df)
