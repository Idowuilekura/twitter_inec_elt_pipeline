# Twitter INEC Analysis ELT Pipeline

## Motivation
Recently, the outcome of the 2023 presidential election in Nigeria has sparked heated debates among Nigerians and foreigners. Many Nigerians have taken to social media, particularly Twitter, to express their frustrations towards the Independent National Electoral Commission (INEC) for the results. Understanding the sentiment about INEC on social media is very important. Hence, the aim of the project is to build an automated data pipeline that will collect tweets that mention INEC and analyze the content of the tweet daily.

The analysis can help inform the Government about the perception of her citizen towards INEC, and seek ways to salvage the situation. In order to conduct a quality analysis, I used the SNSCRAPE tool to scrape older tweets, since the free version of the twitter API can't produce this. 

## Architectural Diagram 
![image](https://user-images.githubusercontent.com/38056084/234894304-b945ea2f-7042-4864-98aa-4e5c9ab01006.png)

### Architectural Diagram Explanation
Tweets containing "INEC" or "inec" were scraped from Twitter, and the data was then loaded into a pandas dataframe. To optimize storage and query performance, the data was stored as a Parquet file on Google Cloud Storage. Parquet, known for its columnar storage format and efficient compression algorithms, was chosen to minimize storage costs and maximize query speed.

Apache Spark (on Google DataProc) was used to load and perform minor transformations such as removal of URLs, hashtags, and emojis. Once the transformations were completed, the data was moved into a Google BigQuery table. DBT was used for heavy transformation and analysis, and the transformed data was written back to BigQuery.

Google LookerStudio was used for analysis and visualization. The steps from ingesting the data up to DBT were orchestrated by Prefect at 12 am daily and ran on Google Cloud Platform. The data refresh rate on Looker Studio was 12 hours.

### Data Visualization Motivation
Given that the project aimed to get the perception of twitter users about INEC and also see how the perception grows over time. My final visualization was composed of the information below, 

- date that the tweet was made
- tweet content 
- username of user that made the tweet
- verified status of the user that made the tweet
- number of the retweets on a tweet
- number of likes on a tweet
- influencer status of the user. This is gotten by dividing the number of users the tweet author is following by those that are following the author. Values less than one means that the user is an influencer. 
- sentiment of each tweet
-  if the tweet was made before the presidential election (which was on February 25th 2023)

Hence the final table that was used for visualizing the data is shown below
|**Field Name**              |**Description**                                       |**Type** |
|----------------------------|------------------------------------------------------|---------|
|date_of_tweet               |The date the tweet was made                           |TIMESTAMP|
|twitter_text                |Content of the Tweet                                  |STRING   |
|username                    |username of the tweet author                          |STRING   |
|user_is_verified            |verified status of the user                           |BOOLEAN  |
|number_of_retweet_count     |the number of count on the tweet                      |INTEGER  |
|user_is_influencer          |influencer status of the user                         |STRING   |
|tweet_sentiment             |sentiment of the tweet                                |STRING   |
|before_presidential_election|if the tweet was made before the presidential election|STRING   |

### Visualization


## How to run the Project on your personal system
To run the project locally, on your system, you will need to install tools such as 
- [Terraform](https://www.terraform.io/). This is for automating the creation of applications on Google cloud
- [Google Cloud Account](https://cloud.google.com/)
- Data Build Tools (DBT) for transformation. 
- Python 

### Steps to replicate it locally 
- Once you have terraform installed on your system
- Clone the repository to your system and cd into the folder
- Go to Google Cloud and create a service account. Ensure the service account has storage admin, storage object admin, google bigquery admin, dataproc adminstrator, dataproc service agent role. Also, ensure you grant the compute storage admin, compute object admin to a service accont with name ********-compute@developer.gserviceaccount.com (this is required for dataproc).
- Generate the service account key as Json, you can rename it to service_account.json. 
- In your terminal type this  ``` export GOOGLE_APPLICATION_CREDENTIALS="path_to_your_service_account.json" ```
- cd into the terraform folder 
- type `terraform apply` in your terminal, click on enter and type yes. The neccessary infrastructure has been provisioned on Google Cloud.
- change directory into twitter inec project, and type `make instal` on your terminal to create the virtual environment and download the neccessary tools that is needed. Ensure you change the `shell which python3` to `shell which python` if you have python installed. Alternatively, you can just type   `pip install requirements.txt`, to install the packages on your system. 
- Change the directory into dbt_idowu_project_zoomcamp and, move into twitter_analysis_tweepy. Go to the `profiles.yml` file, change the project id to your id, google_bigquery dataset to your preferred name and the location to your preferred location.
- change the directory into models/raw. Modify the `schema.yml` file by changing the database name to your googleaccountprojectid, and schema to what you specified earlier. 
- Change the directory back to the twitter_inec_project. Create a file `auth_keys.py` for storing the twitter api authentication, you can get the authetication key from [twitter developer](https://developer.twitter.com/en/docs/developer-portal/overview).
The file should look like this, 
```py
import tweepy
auth = tweepy.OAuthHandler("*********","*****")
auth.set_access_token("***********","*********")
api = tweepy.API(auth,wait_on_rate_limit=True) 
```

```py
DATA_PROC_CLUSTER_NAME='yourdataprocname'
GCP_BUCKET_NAME='your_gcp_bucket_name(the one created by terraform)'
DATAPROC_CLUSTER_REGION='the_region_that_your_dataproc_cluster_is_on'
DATASET_LOCATION = 'your preferred bigquery dataset location'
PROJECT_NAME='your google account project name'
DATASET_NAME='your preferred bigquery dataset name'
TABLE_NAME='your prefered bigquery table name'
```
- The next step is to start the prefect server with `prefect server start`, set the api url. Move back into the twitter_inec_project directory and run `python twitter_flow.py or python3 twitter_flow.py`. This will automatically run all the flows and ingest the data into bigquery.

- To visualize the data, go to lookerstudio. Duplicate the visual, and connect the `core_tweet_data` table as a source to the data. The visuals will automatically be populated.
- For the `top 10 common words in the tweet chart`, you need to click on `Add data` icon, select Bigquery Custom SQL and type this in the editor 
```sql
WITH word_selected AS (SELECT
  lower(word) word 
FROM (
  SELECT
    SPLIT(twitter_text, ' ') as words
  FROM
    `yourprojectname.yourdatasetname.core_tweet_data`
)
CROSS JOIN
  UNNEST(words) as word
WHERE
  LOWER(word) NOT IN ('the','to','of','and','where','com','in','is','a','inec','for','that','not','be','on','as','this','has','are','you','by','will','was','with','have','they','i','from','it','he','&amp;','his','what','we','all','their','at','no','just','an','our','do','can','but','-','your','his','should','stop', 'the', 'to', 'and', 'a', 'in', 'it', 'is', 'I', 'that', 'had', 'on', 'for', 'were', 'was','i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't") and word != ''
)

SELECT word, COUNT(*) as count
FROM word_selected
GROUP BY word
ORDER BY
  count DESC
LIMIT
  20;

```
- Once you are done, you will see a visual similar to what is shown below
![image](https://user-images.githubusercontent.com/38056084/235382225-cf02823e-51f7-472a-a618-bedd71237069.png)

## Next step
- Containerize the workflow and run on Kubernetes
- Implement a CI/CD framework for testing and continuously deploying the code

