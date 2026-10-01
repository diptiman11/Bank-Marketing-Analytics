DROP TABLE IF EXISTS fact_campaign;
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_month;
DROP TABLE IF EXISTS dim_customer;

CREATE TABLE dim_customer (
    customer_id VARCHAR(16) PRIMARY KEY,
    age INTEGER NOT NULL CHECK (age >= 18),
    age_band VARCHAR(16) NOT NULL,
    job VARCHAR(32) NOT NULL,
    marital VARCHAR(16) NOT NULL,
    education VARCHAR(32) NOT NULL,
    balance NUMERIC(12, 2) NOT NULL,
    balance_band VARCHAR(32) NOT NULL,
    credit_default VARCHAR(8) NOT NULL,
    housing_loan VARCHAR(8) NOT NULL,
    personal_loan VARCHAR(8) NOT NULL
);

CREATE TABLE dim_month (
    month_number INTEGER PRIMARY KEY CHECK (month_number BETWEEN 1 AND 12),
    month_name VARCHAR(12) NOT NULL UNIQUE
);

CREATE TABLE dim_channel (
    channel_id INTEGER PRIMARY KEY,
    contact_channel VARCHAR(24) NOT NULL UNIQUE
);

CREATE TABLE fact_campaign (
    contact_id BIGINT PRIMARY KEY,
    customer_id VARCHAR(16) NOT NULL REFERENCES dim_customer(customer_id),
    month_number INTEGER NOT NULL REFERENCES dim_month(month_number),
    channel_id INTEGER NOT NULL REFERENCES dim_channel(channel_id),
    contact_day INTEGER NOT NULL CHECK (contact_day BETWEEN 1 AND 31),
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds >= 0),
    campaign_contacts INTEGER NOT NULL CHECK (campaign_contacts >= 1),
    days_since_previous INTEGER NOT NULL,
    previous_contacts INTEGER NOT NULL CHECK (previous_contacts >= 0),
    previous_outcome VARCHAR(16) NOT NULL,
    subscribed INTEGER NOT NULL CHECK (subscribed IN (0, 1))
);

CREATE INDEX idx_fact_campaign_customer ON fact_campaign(customer_id);
CREATE INDEX idx_fact_campaign_month ON fact_campaign(month_number);
CREATE INDEX idx_fact_campaign_channel ON fact_campaign(channel_id);
CREATE INDEX idx_fact_campaign_subscribed ON fact_campaign(subscribed);

