"""
Bước 1 – Làm sạch dữ liệu Olist bằng pandas và nạp vào cơ sở dữ liệu SQLite.

Đầu vào : data/raw/*.csv (8 bảng của bộ dữ liệu Olist)
Đầu ra  : data/processed/*.csv (bảng đã làm sạch)
          data/olist.db (SQLite, dùng cho các truy vấn trong thư mục sql/)
          outputs/tables/data_quality_log.csv (nhật ký làm sạch)
Chạy    : python src/01_clean_load.py
"""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
(ROOT / "outputs" / "tables").mkdir(parents=True, exist_ok=True)

log = []  # ghi lại từng bước làm sạch: bảng, vấn đề, số dòng bị ảnh hưởng


def note(table, issue, n):
    log.append({"bang": table, "van_de": issue, "so_dong": int(n)})


# ---------------------------------------------------------------- 1. Đọc dữ liệu thô
orders = pd.read_csv(RAW / "olist_orders_dataset.csv")
items = pd.read_csv(RAW / "olist_order_items_dataset.csv")
payments = pd.read_csv(RAW / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(RAW / "olist_order_reviews_dataset.csv")
customers = pd.read_csv(RAW / "olist_customers_dataset.csv")
products = pd.read_csv(RAW / "olist_products_dataset.csv")
sellers = pd.read_csv(RAW / "olist_sellers_dataset.csv")
cat_trans = pd.read_csv(RAW / "product_category_name_translation.csv")

# ---------------------------------------------------------------- 2. Orders: kiểu ngày & ngày giao bị thiếu
date_cols = [c for c in orders.columns if c.startswith("order_") and c not in ("order_id", "order_status")]
for c in date_cols:
    orders[c] = pd.to_datetime(orders[c], errors="coerce")

missing_deliv = orders["order_delivered_customer_date"].isna()
note("orders", "Thiếu ngày giao cho khách (tất cả trạng thái)", missing_deliv.sum())

# Đơn có trạng thái 'delivered' nhưng thiếu ngày giao -> không đo được thời gian giao, gắn cờ để loại khỏi phân tích giao hàng
bad_delivered = (orders["order_status"] == "delivered") & missing_deliv
note("orders", "Trạng thái 'delivered' nhưng thiếu ngày giao (gắn cờ, loại khỏi phân tích giao hàng)", bad_delivered.sum())

orders["is_delivered"] = (orders["order_status"] == "delivered") & ~missing_deliv
orders["delivery_days"] = (orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]).dt.total_seconds() / 86400
late = orders["order_delivered_customer_date"].dt.normalize() > orders["order_estimated_delivery_date"].dt.normalize()
# is_late: 1 = giao trễ, 0 = đúng hạn, rỗng = chưa giao (kiểu Int64 cho phép giá trị rỗng)
orders["is_late"] = late.astype("Int64").where(orders["is_delivered"])
orders["delivery_days"] = orders["delivery_days"].where(orders["is_delivered"])
orders["is_delivered"] = orders["is_delivered"].astype(int)
orders["purchase_month"] = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)

# ---------------------------------------------------------------- 3. Reviews: một đơn có nhiều đánh giá -> giữ đánh giá mới nhất
reviews["review_answer_timestamp"] = pd.to_datetime(reviews["review_answer_timestamp"])
n_before = len(reviews)
reviews = (reviews.sort_values("review_answer_timestamp")
                  .drop_duplicates(subset="order_id", keep="last"))
note("reviews", "Đơn có nhiều đánh giá – giữ đánh giá mới nhất", n_before - len(reviews))
reviews = reviews[["order_id", "review_score", "review_answer_timestamp"]]

# ---------------------------------------------------------------- 4. Products: sửa tên cột, chuẩn hóa danh mục
products = products.rename(columns={"product_name_lenght": "product_name_length",
                                    "product_description_lenght": "product_description_length"})
note("products", "Sửa tên cột viết sai chính tả ('lenght' -> 'length')", 2)

note("products", "Thiếu danh mục sản phẩm -> gán 'unknown'", products["product_category_name"].isna().sum())
products["product_category_name"] = products["product_category_name"].fillna("unknown")

products = products.merge(cat_trans, on="product_category_name", how="left")
no_trans = products["product_category_name_english"].isna() & (products["product_category_name"] != "unknown")
note("products", "Danh mục chưa có bản dịch tiếng Anh -> dịch thủ công", no_trans.sum())
manual = {"pc_gamer": "pc_gamer", "portateis_cozinha_e_preparadores_de_alimentos": "kitchen_portables_and_food_preparers"}
products["product_category_name_english"] = (products["product_category_name_english"]
                                              .fillna(products["product_category_name"].map(manual))
                                              .fillna("unknown"))
# Chuẩn hóa: chữ thường, thay '_' bằng khoảng trắng để hiển thị trên báo cáo
products["category"] = products["product_category_name_english"].str.replace("_", " ").str.strip().str.lower()

# ---------------------------------------------------------------- 5. Kiểm tra trùng lặp ở các bảng còn lại
for name, df, key in [("orders", orders, ["order_id"]), ("customers", customers, ["customer_id"]),
                      ("items", items, ["order_id", "order_item_id"]),
                      ("payments", payments, ["order_id", "payment_sequential"])]:
    note(name, f"Bản ghi trùng theo khóa {key}", df.duplicated(subset=key).sum())

# Giá trị thanh toán = 0 (voucher không hợp lệ) -> loại
zero_pay = payments["payment_value"] <= 0
note("payments", "Giá trị thanh toán <= 0 -> loại", zero_pay.sum())
payments = payments[~zero_pay]

# ---------------------------------------------------------------- 6. Lưu kết quả
tables = {
    "orders": orders.drop(columns=[]),
    "order_items": items,
    "payments": payments,
    "reviews": reviews,
    "customers": customers,
    "products": products[["product_id", "product_category_name", "category", "product_weight_g"]],
    "sellers": sellers,
}
db = ROOT / "data" / "olist.db"
db.unlink(missing_ok=True)
with sqlite3.connect(db) as con:
    for name, df in tables.items():
        out = df.copy()
        for c in out.select_dtypes("datetime").columns:
            out[c] = out[c].dt.strftime("%Y-%m-%d %H:%M:%S")
        out.to_sql(name, con, index=False)
        out.to_csv(PROC / f"{name}.csv", index=False)

pd.DataFrame(log).to_csv(ROOT / "outputs" / "tables" / "data_quality_log.csv", index=False)
print(pd.DataFrame(log).to_string(index=False))
print(f"\nĐã nạp {len(tables)} bảng vào {db.name}")
