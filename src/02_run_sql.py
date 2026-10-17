"""
Bước 2 – Chạy các truy vấn SQL trong thư mục sql/ trên data/olist.db và lưu kết quả ra outputs/tables/.
Kết quả RFM (05_rfm.sql) được ghi ngược vào CSDL thành bảng rfm_customers để 06 tổng hợp.
Chạy: python src/02_run_sql.py
"""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR, OUT = ROOT / "sql", ROOT / "outputs" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(ROOT / "data" / "olist.db") as con:
    for f in sorted(SQL_DIR.glob("*.sql")):
        df = pd.read_sql_query(f.read_text(encoding="utf-8"), con)
        df.to_csv(OUT / f"{f.stem}.csv", index=False)
        if f.stem == "05_rfm":
            # Lưu bảng RFM vào CSDL để truy vấn tổng hợp phía sau dùng lại
            df.to_sql("rfm_customers", con, index=False, if_exists="replace")
            print(f"{f.name}: {len(df):,} khách hàng")
        else:
            print(f"\n== {f.name}\n{df.head(12).to_string(index=False)}")
