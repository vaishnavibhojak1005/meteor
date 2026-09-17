SELECT payment_status, COUNT(*) as count
FROM meteor_db.orders_processed
GROUP BY payment_status
