-- 03. Doanh thu theo danh mục: xếp hạng (RANK) và tỷ trọng lũy kế (Pareto)
WITH cat AS (
    SELECT p.category                          AS danh_muc,
           COUNT(DISTINCT o.order_id)          AS so_don,
           SUM(i.price)                        AS doanh_thu_hang
    FROM orders o
    JOIN order_items i ON i.order_id  = o.order_id
    JOIN products    p ON p.product_id = i.product_id
    WHERE o.is_delivered = 1
      AND o.purchase_month BETWEEN '2017-01' AND '2018-08'
    GROUP BY p.category
)
SELECT RANK() OVER (ORDER BY doanh_thu_hang DESC)                                   AS hang,
       danh_muc,
       so_don,
       ROUND(doanh_thu_hang, 2)                                                     AS doanh_thu_hang,
       ROUND(100.0 * doanh_thu_hang / SUM(doanh_thu_hang) OVER (), 2)               AS ty_trong_pct,
       ROUND(100.0 * SUM(doanh_thu_hang) OVER (ORDER BY doanh_thu_hang DESC
                                               ROWS UNBOUNDED PRECEDING)
             / SUM(doanh_thu_hang) OVER (), 2)                                      AS ty_trong_luy_ke_pct
FROM cat
ORDER BY hang;
