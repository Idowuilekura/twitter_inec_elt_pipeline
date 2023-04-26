{{ config(materialized = 'view') }}
SELECT * 
    FROM {{ source('raw', 'twitter_inec_table_tweepy')}}