import prefect
from prefect import flow, task
# from prefect.core.parameter import DateTimeParameter
# from prefect.schedules  import IntervalSchedule
import pendulum
import os


@task
def upload_files_to_gcloud():
    os.system("gsutil cp download_twitter_data_tweepy.py gs://dtc_data_lake_idowupluralproj/twitter_folder_tweepy/download_twitter_data_tweepy.py")
    os.system("gsutil cp clean_data_spark_tweepy.py gs://dtc_data_lake_idowupluralproj/twitter_folder_tweepy/clean_data_spark_tweepy.py")

@task
def submit_on_dataproc():
    os.system("gcloud dataproc jobs submit pyspark --cluster=idowudataproccluster --region=europe-west4 --jars=gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar --files gs://dtc_data_lake_idowupluralproj/twitter_folder_tweepy/download_twitter_data_tweepy.py gs://dtc_data_lake_idowupluralproj/twitter_folder_tweepy/clean_data_spark_tweepy.py")

@task
def run_dbt_job():
    get_cwd = os.getcwd()
    os.chdir('/home/idowuilekura/Desktop/dataengineering_zoomcamp/twitter_zoomcamp_project/dbt_idowu_project_zoomcamp/twitter_analysis_tweepy')
    os.system('dbt build -t dev')
    os.chdir(get_cwd)



@flow
def run_flow():
    upload_files_to_gcloud()
    submit_on_dataproc()
    run_dbt_job()

run_flow()


# with Flow("parametrized_dt_flow") as flow:
#     sched_start_time = get_scheduled_start_time()
#     print_val(sched_start_time)
#     dt_param_value = DateTimeParameter("some_dt", required=False)
#     determine_parameter_to_use(sched_start_time, dt_param_value)
