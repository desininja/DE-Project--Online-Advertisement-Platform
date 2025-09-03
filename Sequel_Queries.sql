CREATE TABLE online_ads.ads(
    text TEXT,
    category TEXT,
    keywords TEXT,
    campaign_id TEXT,
    status TEXT,
    cpm DECIMAL,
    current_slot_budget DECIMAL,
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
    date_range_start TEXT,
    date_range_end TEXT,
    time_range_start TEXT,
    time_range_end TEXT
);




dROP TABLE online_ads.ads;

SELECT * FROM online_ads.ads;


-- Creating User Table:

CREATE TABLE online_ads.user(
    id TEXT Primary Key,
    age INT,
    gender TEXT,
    internet_usage TEXT,
    income_bukcet TEXT,
    user_agent_string TEXT,
    device_type TEXT,
    websites TEXT,
    movies TEXT,
    music TEXT,
    program TEXT,
    books TEXT,
    negatives TEXT,
    positives TEXT
)

Select * from online_ads.served_ads



CREATE TABLE online_ads.ads(
    text TEXT,
    category TEXT,
    keywords TEXT,
    campaign_id TEXT,
    status TEXT,
    cpm DECIMAL,
    current_slot_budget DECIMAL,
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
    date_range_start TEXT,
    date_range_end TEXT,
    time_range_start TEXT,
    time_range_end TEXT
);

ALTER TABLE online_ads.ads ADD PRIMARY KEY (campaign_id);


CREATE TABLE online_ads.user(
    id TEXT Primary Key,
    age INT,
    gender TEXT,
    internet_usage TEXT,
    income_bukcet TEXT,
    user_agent_string TEXT,
    device_type TEXT,
    websites TEXT,
    movies TEXT,
    music TEXT,
    program TEXT,
    books TEXT,
    negatives TEXT,
    positives TEXT
)



SELECT count(*) FROM online_ads.ads
LIMIT 100


Truncate Table online_ads.ads;

DROP TABLE online_ads.ads;

select * from online_ads.user;

select * from online_ads.ads
WHERE campaign_id = 'b1b99ac4-872f-11f0-b7f6-0e087721c0e9'


Update online_ads.ads
SET current_slot_budget = 10.000002, status = 'Active'
WHERE campaign_id = 'b1b99ac4-872f-11f0-b7f6-0e087721c0e9'



select * from online_ads.ads
where status = 'Active'


select * from online_ads.ads
where campaign_id ='b1b99ac4-872f-11f0-b7f6-0e087721c0e9'



CREATE TABLE online_ads.ads(
    text TEXT,
    category TEXT,
    keywords TEXT,
    campaign_id TEXT,
    status TEXT,
    cpm DECIMAL,
    current_slot_budget DECIMAL,
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
    date_range_start TEXT,
    date_range_end TEXT,
    time_range_start TEXT,
    time_range_end TEXT
);

ALTER TABLE online_ads.ads ADD PRIMARY KEY (campaign_id);


CREATE TABLE online_ads.user(
    id TEXT Primary Key,
    age INT,
    gender TEXT,
    internet_usage TEXT,
    income_bukcet TEXT,
    user_agent_string TEXT,
    device_type TEXT,
    websites TEXT,
    movies TEXT,
    music TEXT,
    program TEXT,
    books TEXT,
    negatives TEXT,
    positives TEXT
)