# Hướng dẫn dựng dashboard Power BI – Olist

Thời gian ước tính: 60–90 phút. Cần Power BI Desktop (Windows, miễn phí).

## 1. Nạp dữ liệu

`Home > Get data > Text/CSV`, nạp 4 file trong `powerbi/data/`:

| Bảng | Loại | Khóa |
|---|---|---|
| `fact_orders` | Bảng sự kiện (1 dòng / đơn) | `order_id`, `customer_unique_id`, `purchase_date` |
| `fact_order_items` | Bảng sự kiện (1 dòng / sản phẩm trong đơn) | `order_id` |
| `dim_customer_rfm` | Bảng chiều khách hàng + RFM | `customer_unique_id` |
| `dim_date` | Bảng chiều ngày | `date` |

Trong Power Query: kiểm tra `purchase_date` và `dim_date[date]` có kiểu **Date**; `revenue`, `price` kiểu **Decimal Number**.

## 2. Mô hình dữ liệu (Model view)

- `dim_date[date]` 1 ─── * `fact_orders[purchase_date]`
- `dim_customer_rfm[customer_unique_id]` 1 ─── * `fact_orders[customer_unique_id]`
- `fact_orders[order_id]` 1 ─── * `fact_order_items[order_id]` (hướng lọc: Single)
- Chọn bảng `dim_date` > `Mark as date table` > cột `date`.

## 3. Measure

Dán các measure trong `measures.dax`.

## 4. Bố cục dashboard (3 trang)

**Trang 1 – Tổng quan doanh số**
- 4 thẻ KPI: `Doanh thu`, `So don`, `So khach`, `Gia tri don TB`
- Biểu đồ đường: `Doanh thu` theo `dim_date[year_month]`
- Biểu đồ thanh ngang: `Doanh thu hang hoa` theo `fact_order_items[category]` (Top N = 10)
- Slicer: `dim_date[year]`, `fact_orders[customer_state]`

**Trang 2 – Giao hàng & đánh giá**
- Thẻ KPI: `Ty le giao tre`, `So ngay giao TB`, `Diem danh gia TB`
- Biểu đồ cột nhóm: số đơn theo `review_score`, chia theo `is_late`
- Bảng: `customer_state` × `Ty le giao tre`, `Diem danh gia TB` (sắp xếp giảm dần theo tỷ lệ trễ)

**Trang 3 – Phân khúc khách hàng RFM**
- Thẻ KPI: `Ty le khach mua 1 lan`
- Biểu đồ thanh: `So khach` và `Ty trong doanh thu` theo `dim_customer_rfm[phan_khuc]`
- Bảng: phân khúc × số khách, doanh thu, `recency` trung bình

## 5. Đối chiếu số liệu (không lọc gì)

Nếu dựng đúng, dashboard phải ra các con số sau (khớp với kết quả SQL):

| Chỉ số | Giá trị |
|---|---|
| Doanh thu | R$ 15.371.741,09 |
| Số đơn | 96.203 |
| Số khách | 93.096 |
| Giá trị đơn TB | R$ 159,78 |
| Tỷ lệ giao trễ | 6,79% |
| Điểm đánh giá TB – đúng hạn / giao trễ | 4,28 / 2,26 |
| Tỷ lệ khách mua 1 lần | 97,0% |

## 6. Lưu và đưa lên GitHub

Lưu file thành `powerbi/olist_dashboard.pbix`, chụp ảnh 3 trang lưu vào `powerbi/screenshots/`, rồi commit và push.
