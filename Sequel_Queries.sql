CREATE TABLE online_ads.ads(
    text TEXT,
    category TEXT,
    keywords TEXT,
    campaign_id TEXT,
    status TEXT,
    target_gender TEXT,
    target_age_start INT,
    target_age_end INT,
    target_city TEXT,
    target_state TEXT,
    target_country TEXT,
    target_income_bucket TEXT,
    target_device TEXT,
    cpc DECIMAL,
    cpa DECIMAL,
    budget DECIMAL,
    current_slot_budget DECIMAL,
    date_range_start TEXT,
    date_range_end TEXT,
    time_range_start TEXT,
    time_range_end TEXT
);
dROP TABLE online_ads.ads;

SELECT * FROM online_ads.ads;