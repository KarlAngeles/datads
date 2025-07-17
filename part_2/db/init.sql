CREATE TABLE IF NOT EXISTS ad_insights (
  id SERIAL PRIMARY KEY,
  platform TEXT NOT NULL,
  campaign_id TEXT,
  ad_id TEXT NOT NULL,
  date DATE NOT NULL,
  impressions INT,
  clicks INT,
  spend DECIMAL,
  conversions INT,
  revenue DECIMAL,
  ctr DECIMAL,
  cpc DECIMAL,
  roas DECIMAL,
  fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  UNIQUE (platform, ad_id, date)
);

CREATE INDEX idx_ad_insights_date ON ad_insights(date);
