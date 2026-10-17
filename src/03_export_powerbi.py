"""
Bước 3 – Xuất bảng dữ liệu cho dashboard Power BI (mô hình dạng sao).
Đầu ra: powerbi/data/fact_orders.csv, fact_order_items.csv, dim_customer_rfm.csv, dim_date.csv
Chạy  : python src/03_export_powerbi.py
"""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "powerbi" / "data"
OUT.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(ROOT / "data" / "olist.db") as con:
    # Bảng sự kiện cấp đơn hàng: doanh thu, giao hàng, đánh giá
    fact_orders = pd.read_sql_query("""
        SELECT o.order_id,
               c.customer_unique_id,
               c.customer_state,
               DATE(o.order_purchase_timestamp)          AS purchase_date,
               ROUND(SUM(i.price), 2)                    AS product_revenue,
               ROUND(SUM(i.freight_value), 2)            AS freight,
               ROUND(SUM(i.price + i.freight_value), 2)  AS revenue,
               COUNT(*)                                  AS items,
               ROUND(o.delivery_days, 1)                 AS delivery_days,
               o.is_late,
               r.review_score
        FROM orders o
        JOIN order_items i ON i.order_id   = o.order_id
        JOIN customers  c ON c.customer_id = o.customer_id
        LEFT JOIN reviews r ON r.order_id  = o.order_id
        WHERE o.is_delivered = 1
          AND o.purchase_month BETWEEN '2017-01' AND '2018-08'
        GROUP BY o.order_id""", con)

    # Bảng sự kiện cấp dòng sản phẩm: dùng cho phân tích danh mục
    fact_items = pd.read_sql_query("""
        SELECT i.order_id, i.product_id, p.category, i.price, i.freight_value
        FROM order_items i
        JOIN orders   o ON o.order_id   = i.order_id
        JOIN products p ON p.product_id = i.product_id
        WHERE o.is_delivered = 1
          AND o.purchase_month BETWEEN '2017-01' AND '2018-08'""", con)

    # Bảng chiều khách hàng kèm điểm và phân khúc RFM
    dim_customer = pd.read_sql_query("SELECT * FROM rfm_customers", con)

# Bảng chiều ngày (đầy đủ ngày trong giai đoạn) – đánh dấu là Date table trong Power BI
dates = pd.date_range("2017-01-01", "2018-08-31", freq="D")
dim_date = pd.DataFrame({"date": dates.date, "year": dates.year, "month": dates.month,
                         "year_month": dates.strftime("%Y-%m"), "quarter": "Q" + dates.quarter.astype(str)})

for name, df in [("fact_orders", fact_orders), ("fact_order_items", fact_items),
                 ("dim_customer_rfm", dim_customer), ("dim_date", dim_date)]:
    df.to_csv(OUT / f"{name}.csv", index=False)
    print(f"{name:18s} {len(df):>8,} dòng")
