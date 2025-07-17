1. Celery Beat triggers fetch_facebook_insights_group every day.

2. Celery Worker runs a group task:

- Each subtask calls the Facebook-like API for a specific campaign_id.

- Handles pagination, rate limiting, and retries.

3. Fetched data is:

- Transformed (CTR, CPC, ROAS).

- Inserted into the PostgreSQL database.