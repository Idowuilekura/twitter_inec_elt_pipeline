{{config(materialized='view')}}
SELECT DISTINCT *
    FROM 
    {{ ref('stg_tweet_data') }}
