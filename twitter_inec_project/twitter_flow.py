import prefect
from prefect import flow, task
# from prefect.core.parameter import DateTimeParameter
# from prefect.schedules  import IntervalSchedule
import pendulum
import os
from download_twitter_data_tweepy import tweets_df
import datetime as dt
from dotenv import load_dotenv


load_dotenv()

date_yesterday = (dt.datetime.now().date()- dt.timedelta(1)).strftime("%Y-%m-%d")
dataproc_cluster_name = os.getenv('DATA_PROC_CLUSTER_NAME')
# # dataproc_cluster_name = 'datazoomidcluster'
# print(type(dataproc_cluster_name))
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
DATAPROC_CLUSTER_REGION = os.getenv("DATAPROC_CLUSTER_REGION")

@task
def upload_files_to_gcloud(GCP_BUCKET_NAME: str):
    os.system(f"gsutil cp download_twitter_data_tweepy.py {GCP_BUCKET_NAME}/twitter_folder_tweepy/download_twitter_data_tweepy.py")
    os.system(f"gsutil cp clean_data_spark_tweepy.py {GCP_BUCKET_NAME}/twitter_folder_tweepy/clean_data_spark_tweepy.py")

@task
def download_twitter_data_upload_to_storage(GCP_BUCKET_NAME:str):
    tweets_df.to_parquet(f'{GCP_BUCKET_NAME}/twitter_data/data_{date_yesterday}.parquet.gzip',compression='gzip')

@task
def submit_on_dataproc(GCP_BUCKET_NAME):
    os.system(f"gcloud dataproc jobs submit pyspark --cluster={dataproc_cluster_name} --region={DATAPROC_CLUSTER_REGION} --jars=gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar {GCP_BUCKET_NAME}/twitter_folder_tweepy/clean_data_spark_tweepy.py")

@task
def run_dbt_job():
    get_cwd = os.getcwd()
    os.chdir('../dbt_idowu_project_zoomcamp/twitter_analysis_tweepy')
    os.system('dbt build -t dev')
    os.chdir(get_cwd)



@flow
def twitter_flow(GCP_BUCKET_NAME:str,name='my_twitter_flow'):
    upload_files_to_gcloud(GCP_BUCKET_NAME=GCP_BUCKET_NAME)
    download_twitter_data_upload_to_storage(GCP_BUCKET_NAME=GCP_BUCKET_NAME)
    submit_on_dataproc(GCP_BUCKET_NAME=GCP_BUCKET_NAME)
    run_dbt_job()

if __name__ == "__main__":
    twitter_flow(GCP_BUCKET_NAME=GCP_BUCKET_NAME)

