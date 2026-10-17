-- 02. Doanh thu theo tháng, tăng trưởng so với tháng trước (LAG) và doanh thu lũy kế (SUM OVER)
WITH monthly AS (
    SELECT o.purchase_month                       AS thang,
           COUNT(DISTINCT o.order_id)             AS so_don,
           SUM(i.price + i.freight_value)         AS doanh_thu
    FROM orders o
    JOIN order_items i ON i.order_id = o.order_id
    WHERE o.is_delivered = 1
      AND o.purchase_month BETWEEN '2017-01' AND '2018-08'
    GROUP BY o.purchase_month
)
SELECT thang,
       so_don,
       ROUND(doanh_thu, 2)                                                        AS doanh_thu,
       ROUND(100.0 * (doanh_thu - LAG(doanh_thu) OVER (ORDER BY thang))
             / LAG(doanh_thu) OVER (ORDER BY thang), 1)                            AS tang_truong_mom_pct,
       ROUND(SUM(doanh_thu) OVER (ORDER BY thang), 2)                              AS doanh_thu_luy_ke
FROM monthly
ORDER BY thang;
