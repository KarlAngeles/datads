# Ad Insights Aggregator (Facebook)

This project fetches advertising data (insights) from the Facebook Ads mock API and stores the results in a PostgreSQL database. The system is designed to support multiple ad campaigns and is easily extensible to support other ad platforms in the future.

## Features

- Fetches impressions, clicks, spend, revenue, conversions, and computes CTR, CPC, and ROAS
- Supports multiple Facebook campaign IDs
- Automatically paginates through results
- Scheduled via Celery Beat
- Retries on failure or rate limits
- Dockerized environment

## Requirements

- Docker + Docker Compose

## Setup

1. Clone the repository:
    ```
    git clone https://github.com/KarlAngeles/datads.git
    cd datads/part_2
    ```

2. Build and run everything:
    ```
    docker-compose up --build
    ```