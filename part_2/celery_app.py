from celery import Celery
from celery.schedules import crontab
import os

app = Celery("ads_insights", broker=os.getenv("CELERY_BROKER_URL"), include=["ad_tasks.poller"])

app.conf.timezone = "UTC"
app.conf.enable_utc = True

app.conf.beat_schedule = {
    "fetch-fb-daily": {
        "task": "ad_tasks.poller.fetch_all_facebook_campaigns",
        "schedule": crontab(minute=0, hour=0),
        "args": [],
    },
}