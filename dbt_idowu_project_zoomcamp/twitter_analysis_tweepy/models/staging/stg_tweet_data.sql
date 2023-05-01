{{ config(materialized = 'view') }}

WITH raw_tweets AS (
    SELECT *
        FROM {{ ref('raw_tweepy_twitter_data') }} 
),

influencer_calculation AS (
    SELECT username, CASE WHEN number_of_followers > 0 and number_of_followers >5000 THEN number_of_following/number_of_followers 
    ELSE 1 END AS influencer_index
    FROM  raw_tweets
),

influencer_index_average AS (SELECT username, AVG(influencer_index) average_influencer_index
        FROM influencer_calculation
        GROUP BY username),

    influencer_name AS (SELECT username, CASE WHEN average_influencer_index < 1 THEN 'Influencer'
    ELSE 'Non-influencer' END AS user_is_influencer
    FROM influencer_index_average), distinct_datetime AS (
        SELECT DISTINCT(datetime) time_tweet_was_made
        FROM raw_tweets
    ), 
    
    date_before_or_after_president_election AS (
        SELECT time_tweet_was_made, CASE WHEN time_tweet_was_made <= '2023-02-25 07:00:00' THEN 'Yes'
        ELSE 'No' END AS before_presidential_election
        FROM distinct_datetime
    )

SELECT rt.datetime date_of_tweet, rt.twitter_text, rt.username, CASE WHEN rt.user_is_verified = TRUE THEN 'Verified' 
ELSE 'Not-Verified' END AS user_is_verified,rt.number_of_retweet_count,
    rt.number_of_tweet_like,iia.user_is_influencer user_is_influencer,
CASE WHEN CAST(rt.tweet_sentiment AS INTEGER) = 1 THEN 'Positive'
    WHEN CAST(rt.tweet_sentiment AS INTEGER) = 0 THEN 'Neutral'
    ELSE 'Negative' END AS tweet_sentiment, dboape.before_presidential_election before_presidential_election

    FROM raw_tweets rt
    INNER JOIN influencer_name iia 
    ON rt.username = iia.username 
    INNER JOIN 
    date_before_or_after_president_election dboape 
    ON rt.datetime = dboape.time_tweet_was_made
