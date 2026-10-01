-- 1. Overall campaign conversion
SELECT
    COUNT(*) AS contacts,
    SUM(subscribed) AS subscriptions,
    ROUND(AVG(subscribed::numeric) * 100, 2) AS conversion_rate_pct
FROM fact_campaign;

-- 2. Conversion by customer occupation
SELECT
    c.job,
    COUNT(*) AS contacts,
    SUM(f.subscribed) AS subscriptions,
    ROUND(AVG(f.subscribed::numeric) * 100, 2) AS conversion_rate_pct
FROM fact_campaign AS f
JOIN dim_customer AS c USING (customer_id)
GROUP BY c.job
HAVING COUNT(*) >= 100
ORDER BY conversion_rate_pct DESC;

-- 3. Channel performance
SELECT
    ch.contact_channel,
    COUNT(*) AS contacts,
    ROUND(AVG(f.subscribed::numeric) * 100, 2) AS conversion_rate_pct
FROM fact_campaign AS f
JOIN dim_channel AS ch USING (channel_id)
GROUP BY ch.contact_channel
ORDER BY conversion_rate_pct DESC;

-- 4. Monthly campaign performance
SELECT
    m.month_number,
    m.month_name,
    COUNT(*) AS contacts,
    ROUND(AVG(f.subscribed::numeric) * 100, 2) AS conversion_rate_pct
FROM fact_campaign AS f
JOIN dim_month AS m USING (month_number)
GROUP BY m.month_number, m.month_name
ORDER BY m.month_number;

-- 5. Contact-frequency saturation
SELECT
    CASE
        WHEN campaign_contacts = 1 THEN '1 contact'
        WHEN campaign_contacts = 2 THEN '2 contacts'
        WHEN campaign_contacts BETWEEN 3 AND 4 THEN '3-4 contacts'
        ELSE '5+ contacts'
    END AS contact_intensity,
    COUNT(*) AS contacts,
    ROUND(AVG(subscribed::numeric) * 100, 2) AS conversion_rate_pct
FROM fact_campaign
GROUP BY contact_intensity
ORDER BY MIN(campaign_contacts);

