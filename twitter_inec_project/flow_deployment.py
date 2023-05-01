from twitter_flow import twitter_flow

from prefect.deployments import Deployment 
from prefect.server.schemas.schedules import CronSchedule

deployment = Deployment.build_from_flow(
    flow=twitter_flow,
    name='my_twitter_flow',
    version=1,
    work_queue_name="test",
    schedule=(CronSchedule(cron='0 5 * * *', timezone='Africa/Lagos'))
)

deployment.apply()