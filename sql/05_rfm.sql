-- 05. Phân khúc khách hàng RFM (Recency – Frequency – Monetary)
--  * Khách hàng định danh bằng customer_unique_id (một người có thể có nhiều customer_id)
--  * Ngày tham chiếu = ngày mua cuối cùng trong giai đoạn + 1 ngày
--  * R và M chấm điểm 1–5 bằng NTILE(5); F chấm theo số đơn vì phần lớn khách chỉ mua 1 lần
WITH order_rev AS (
    SELECT o.order_id,
           c.customer_unique_id,
           DATE(o.order_purchase_timestamp)   AS ngay_mua,
           SUM(i.price + i.freight_value)     AS revenue
    FROM orders o
    JOIN order_items i ON i.order_id   = o.order_id
    JOIN customers  c ON c.customer_id = o.customer_id
    WHERE o.is_delivered = 1
      AND o.purchase_month BETWEEN '2017-01' AND '2018-08'
    GROUP BY o.order_id, c.customer_unique_id, DATE(o.order_purchase_timestamp)
),
ref AS (SELECT DATE(MAX(ngay_mua), '+1 day') AS ref_date FROM order_rev),
rfm AS (
    SELECT customer_unique_id,
           CAST(JULIANDAY((SELECT ref_date FROM ref)) - JULIANDAY(MAX(ngay_mua)) AS INT) AS recency,
           COUNT(*)                                                                    AS frequency,
           ROUND(SUM(revenue), 2)                                                      AS monetary
    FROM order_rev
    GROUP BY customer_unique_id
),
scored AS (
    SELECT *,
           NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,   -- mua càng gần đây điểm càng cao
           NTILE(5) OVER (ORDER BY monetary ASC)  AS m_score,   -- chi tiêu càng nhiều điểm càng cao
           CASE WHEN frequency = 1 THEN 1 WHEN frequency = 2 THEN 4 ELSE 5 END AS f_score
    FROM rfm
)
SELECT *,
       CASE
           WHEN frequency >= 2                    THEN 'Khách mua lặp lại'
           WHEN r_score >= 4 AND m_score >= 4     THEN 'Khách mới giá trị cao'
           WHEN r_score >= 4                      THEN 'Khách mới giá trị thấp'
           WHEN r_score <= 2 AND m_score >= 4     THEN 'Giá trị cao có nguy cơ rời bỏ'
           WHEN r_score <= 2                      THEN 'Ngủ đông'
           ELSE 'Cần chăm sóc'
       END AS phan_khuc
FROM scored;
