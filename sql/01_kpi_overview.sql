-- 01. Chỉ số tổng quan giai đoạn phân tích 01/2017 – 08/2018 (chỉ tính đơn đã giao)
-- Doanh thu đơn hàng = tổng (giá sản phẩm + phí vận chuyển) của các dòng sản phẩm trong đơn
WITH order_rev AS (
    SELECT o.order_id,
           c.customer_unique_id,
           SUM(i.price + i.freight_value) AS revenue
    FROM orders o
    JOIN order_items i ON i.order_id = o.order_id
    JOIN customers  c ON c.customer_id = o.customer_id
    WHERE o.is_delivered = 1
      AND o.purchase_month BETWEEN '2017-01' AND '2018-08'
    GROUP BY o.order_id, c.customer_unique_id
)
SELECT COUNT(*)                                   AS so_don,
       COUNT(DISTINCT customer_unique_id)         AS so_khach,
       ROUND(SUM(revenue), 2)                     AS doanh_thu,
       ROUND(AVG(revenue), 2)                     AS gia_tri_don_tb
FROM order_rev;
