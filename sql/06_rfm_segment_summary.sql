-- 06. Tổng hợp theo phân khúc RFM (đọc từ bảng rfm_customers do 02_run_sql.py tạo từ 05_rfm.sql)
SELECT phan_khuc,
       COUNT(*)                                                      AS so_khach,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)            AS ty_le_khach_pct,
       ROUND(SUM(monetary), 2)                                       AS doanh_thu,
       ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 1)  AS ty_trong_doanh_thu_pct,
       ROUND(AVG(monetary), 2)                                       AS chi_tieu_tb,
       ROUND(AVG(recency), 0)                                        AS recency_tb_ngay
FROM rfm_customers
GROUP BY phan_khuc
ORDER BY doanh_thu DESC;
