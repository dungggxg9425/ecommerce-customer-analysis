-- 04. Giao hàng trễ so với ngày dự kiến ảnh hưởng thế nào đến điểm đánh giá?
SELECT CASE o.is_late WHEN 1 THEN 'Giao trễ' ELSE 'Đúng hạn' END        AS tinh_trang_giao,
       COUNT(*)                                                          AS so_don,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)                AS ty_le_pct,
       ROUND(AVG(o.delivery_days), 1)                                    AS so_ngay_giao_tb,
       ROUND(AVG(r.review_score), 2)                                     AS diem_danh_gia_tb,
       ROUND(100.0 * AVG(CASE WHEN r.review_score <= 2 THEN 1.0 ELSE 0 END), 1) AS ty_le_danh_gia_1_2_sao_pct
FROM orders o
JOIN reviews r ON r.order_id = o.order_id
WHERE o.is_delivered = 1
  AND o.purchase_month BETWEEN '2017-01' AND '2018-08'
GROUP BY o.is_late
ORDER BY o.is_late;
