import os
import requests
import psycopg2
from celery import shared_task, group
from datetime import datetime, timedelta
from urllib.parse import urlencode

API_BASE_URL = os.getenv("API_BASE_URL", "https://datads-mock-ad-apis.happygrass-47d99234.germanywestcentral.azurecontainerapps.io")
API_KEY = os.getenv("FACEBOOK_API_KEY", "facebook_test_key_123")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/datads")
CAMPAIGN_IDS = ["fb_camp_123", "fb_camp_456", "fb_camp_789"]

@shared_task
def fetch_all_facebook_campaigns():
    tasks = []
    for campaign_id in CAMPAIGN_IDS:
        task_sig = fetch_facebook_data.s(campaign_id)
        tasks.append(task_sig)

    job_group = group(tasks)
    job_group.apply_async()

@shared_task(bind=True, max_retries=3, retry_backoff=True, rate_limit="200/h")
def fetch_facebook_data(self, campaign_id, since=None, until=None):
    until = until or datetime.utcnow().date()
    since = since or (until - timedelta(days=30))
    print(f"Fetching data from {since} to {until} for campaign {campaign_id}")

    try:
        insights = _fetch_all_insights(self, campaign_id, since, until)
        for insight in insights:
            _store_insight_row(insight)
    except Exception as e:
        raise self.retry(exc=e)

def _fetch_all_insights(task, campaign_id, since, until):
    insights = []
    after = None

    while True:
        data, after = _fetch_page(task, campaign_id, since, until, after)
        if not data:
            break
        for row in data:
            insights.append(_process_row(row))
        if not after:
            break

    return insights

def _fetch_page(task, campaign_id, since, until, after):
    params = {"since": since, "until": until, "limit": 100}
    if after:
        params["after"] = after

    url = f"{API_BASE_URL}/api/v1/campaigns/{campaign_id}/insights?{urlencode(params)}"
    headers = {"x-api-key": API_KEY}

    res = requests.get(url, headers=headers, timeout=10)

    if res.status_code == 429:
        raise task.retry(exc=Exception("Rate limit hit"), countdown=60)
    elif res.status_code >= 500:
        raise task.retry(exc=Exception("Server error"), countdown=30)

    res.raise_for_status()
    json = res.json()
    return json.get("data", []), json.get("paging", {}).get("next")

def _process_row(row):
    impressions = row["impressions"]
    clicks = row["clicks"]
    spend = row["spend"]
    revenue = row["revenue"]

    return {
        "platform": "facebook",
        "campaign_id": row["campaign_id"],
        "ad_id": row["ad_id"],
        "date": row["date"],
        "impressions": impressions,
        "clicks": clicks,
        "spend": spend,
        "conversions": row["conversions"],
        "revenue": revenue,
        "ctr": round(clicks / impressions, 4) if impressions else 0,
        "cpc": round(spend / clicks, 4) if clicks else 0,
        "roas": round(revenue / spend, 4) if spend else 0,
        "fetched_at": datetime.utcnow(),
    }

def _store_insight_row(insight):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        query = """
            INSERT INTO ad_insights (
                platform, campaign_id, ad_id, date,
                impressions, clicks, spend, conversions, revenue,
                ctr, cpc, roas, fetched_at
            )
            VALUES (
                %(platform)s, %(campaign_id)s, %(ad_id)s, %(date)s,
                %(impressions)s, %(clicks)s, %(spend)s, %(conversions)s, %(revenue)s,
                %(ctr)s, %(cpc)s, %(roas)s, %(fetched_at)s
            )
            ON CONFLICT (platform, ad_id, date) DO UPDATE SET
                impressions = EXCLUDED.impressions,
                clicks = EXCLUDED.clicks,
                spend = EXCLUDED.spend,
                conversions = EXCLUDED.conversions,
                revenue = EXCLUDED.revenue,
                ctr = EXCLUDED.ctr,
                cpc = EXCLUDED.cpc,
                roas = EXCLUDED.roas,
                fetched_at = EXCLUDED.fetched_at;
        """

        cursor.execute(query, insight)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("❌ Insert failed:", e)

    finally:
        cursor.close()
        conn.close()