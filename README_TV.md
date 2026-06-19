# Đăng Khoa Bank

Đăng Khoa Bank là một ứng dụng ngân hàng trên máy tính chuyên nghiệp, sẵn sàng cho môi trường vận hành thực tế, được xây dựng bằng **Python** và **PyQt6**. Ứng dụng sở hữu giao diện người dùng hiện đại theo phong cách Fintech, hệ thống cơ sở dữ liệu cục bộ mạnh mẽ và các công cụ quản trị toàn diện.

## Tổng quan Dự án

Đăng Khoa Bank cung cấp một nền tảng an toàn và trực quan để quản lý tài chính cá nhân. Ứng dụng tập trung vào việc xử lý dữ liệu hiệu năng cao, đảm bảo an toàn giao dịch (tính toàn vẹn giao dịch atomic) và trải nghiệm người dùng cao cấp.

- **Mục đích chính:** Quản lý tài chính cá nhân và giao dịch ngân hàng.
- **Định hướng Fintech:** Giao diện thẩm mỹ ngân hàng số hiện đại tích hợp phân tích biểu đồ trực quan.
- **Mô hình:** Ứng dụng desktop giàu tính năng hoạt động theo cơ chế ngoại tuyến (offline-first) an toàn.

## Các tính năng chính

### Tính năng cho Khách hàng
- **Xác thực an toàn:** Giả lập xác thực đa yếu tố (2FA OTP) và quản lý phiên làm việc tự động đăng xuất khi treo máy.
- **Quản lý Ví:** Theo dõi số dư thời gian thực và quản lý thẻ ngân hàng ảo.
- **Hệ thống chuyển khoản:** Chuyển tiền nội bộ an toàn với tính năng tự động phân giải và hiển thị tên người nhận, xuất biên lai giao dịch điện tử.
- **Thanh toán qua mã QR:** Quét và phân tích mã QR để tự động điền nhanh thông tin chuyển khoản.
- **Hệ thống gửi tiết kiệm:** Nhiều gói tiết kiệm khác nhau với thanh tiến trình tích lũy và công cụ giả lập sinh lãi.
- **Lịch sử giao dịch:** Nhật ký giao dịch chi tiết hỗ trợ tìm kiếm và lọc nâng cao.
- **Phân tích nâng cao:** Biểu đồ tương tác trực quan hóa chi tiêu và tăng trưởng tiết kiệm.
- **Cá nhân hóa:** Hỗ trợ đầy đủ chế độ Sáng/Tối (Light/Dark mode) và đa ngôn ngữ (Tiếng Việt/Tiếng Anh).

### Tính năng cho Quản trị viên (Admin)
- **Dashboard phân tích:** Tổng quan về số liệu thống kê toàn hệ thống và các xu hướng giao dịch.
- **Quản lý người dùng:** Quản lý tài khoản khách hàng, phân hạng thành viên (Tier) và khóa/mở khóa trạng thái tài khoản.
- **Giám sát giao dịch:** Kiểm toán tất cả các giao dịch trong hệ thống theo thời gian thực.
- **Trung tâm bảo mật:** Giám sát gian lận, phân bổ mức độ rủi ro của các giao dịch và kiểm tra sức khỏe hệ thống.
- **Thông báo hệ thống:** Quản lý và gửi thông báo chung đến toàn bộ người dùng.
- **Sao lưu & Phục hồi:** Bảo trì cơ sở dữ liệu và quản lý các ảnh chụp nhanh (snapshot) sao lưu dữ liệu.

## Giao diện & Trải nghiệm người dùng (UI/UX)
- **Thẩm mỹ Fintech:** Thiết kế tối giản, sạch sẽ với tông màu xanh ngọc (cyan) chuyên nghiệp.
- **Hiệu ứng chuyển động:** Các chuyển cảnh mượt mà và phản hồi tương tác tạo cảm giác hiện đại.
- **Bố cục co giãn linh hoạt (Responsive Layout):** Tối ưu hóa hiển thị cho nhiều độ phân giải màn hình khác nhau (từ 1366x768 đến 2K+).
- **Thành phần tùy chỉnh:** Các widget, bảng biểu và biểu đồ tăng trưởng tự vẽ chuyên dụng.
- **Hóa đơn điện tử:** Giao diện hóa đơn đẹp mắt hỗ trợ xuất ra ảnh hoặc file để lưu trữ.

## Cấu trúc dự án

```text
src/
 ├── admin/         # Giao diện quản trị, các tab và dịch vụ quản trị viên
 ├── assets/        # Tài nguyên đồ họa (logo, hình ảnh, icon)
 ├── core/          # Công cụ cốt lõi: cấu hình theme, ngôn ngữ, ổn định hệ thống
 ├── database/      # SQLite schema, quản lý kết nối và các file di cư dữ liệu (migrations)
 ├── design/        # Hệ thống thiết kế: token giao diện, khoảng cách và các widget tùy biến
 ├── models/        # Các mô hình cấu trúc dữ liệu
 ├── security/      # Lớp bảo vệ bảo mật, xác thực và luật kiểm soát đăng nhập
 ├── services/      # Logic nghiệp vụ: chuyển tiền, tiết kiệm, mã QR và biểu đồ phân tích
 └── ui/            # Giao diện chính của người dùng: cửa sổ chính, các tab và widget
```

## Tổng quan kiến trúc

Ứng dụng tuân theo kiến trúc phân tầng hướng dịch vụ (Service-Oriented Architecture):

```text
Tầng Giao diện (PyQt6 UI)
       ↓
Tầng Nghiệp vụ (Business Logic Services)
       ↓
Tầng Cơ sở dữ liệu (SQLite + WAL)
       ↓
Tầng Bảo mật (Auth & Security Guards)
```

## Công nghệ sử dụng
- **Python:** Ngôn ngữ lập trình cốt lõi.
- **PyQt6:** Thư viện lập trình giao diện Desktop hiệu năng cao.
- **SQLite:** Cơ sở dữ liệu cục bộ với chế độ **WAL (Write-Ahead Logging)** để xử lý đọc/ghi đồng thời tối ưu.
- **Qt Charts / QPainter:** Vẽ đồ họa vector và biểu đồ tương tác tùy biến.
- **QSS:** Định dạng phong cách giao diện (tương tự CSS) nhất quán cho toàn app.
- **Pathlib:** Quản lý đường dẫn tệp tin an toàn trên các hệ điều hành khác nhau.

## Hệ thống cơ sở dữ liệu
- **Lưu trữ SQLite:** Quản lý dữ liệu cục bộ an toàn với các giao dịch có tính toàn vẹn (atomic).
- **An toàn giao dịch:** Cơ chế tự động khôi phục dữ liệu (rollback) và WAL để ngăn chặn hỏng dữ liệu khi mất điện hoặc lỗi đột ngột.
- **Tối ưu hóa hiệu năng:** Cấu hình thời gian chờ (timeout) hợp lý và tối ưu hóa câu lệnh PRAGMA cho độ trễ cực thấp.

## Tính năng bảo mật
- **Xác thực:** Quy trình đăng nhập an toàn kết hợp tự động đăng xuất khi treo máy (Session timeout).
- **Kiểm chứng dữ liệu:** Ràng buộc chặt chẽ các trường thông tin cho mọi giao dịch tài chính.
- **Nhật ký hệ thống:** Lưu vết toàn bộ hoạt động quản trị viên để phục vụ kiểm toán bảo mật.
- **Xác thực mã PIN:** Lớp bảo mật thứ hai (mã PIN 6 số) bắt buộc cho các giao dịch nhạy cảm.

## Tiết kiệm & Phân tích
- **Động cơ mô phỏng:** Tính toán thời gian thực lãi suất tích lũy và tiến độ hoàn thành mục tiêu.
- **Dịch vụ phân tích:** Tổng hợp lịch sử giao dịch thành các điểm dữ liệu trực quan trên biểu đồ.

## Hệ thống thanh toán QR
- **Phân tích QR:** Giải mã nội dung mã QR để tự động điền số tài khoản và thông tin người nhận.
- **Điền form tự động:** Giảm thiểu lỗi sai sót do người dùng nhập thủ công số tài khoản.

## Hướng dẫn cài đặt

### Yêu cầu hệ thống
- Python 3.9+
- pip (Trình quản lý thư viện Python)

### Cài đặt nhanh
1. Tải mã nguồn về máy:
   ```bash
   git clone https://github.com/your-repo/dang-khoa-bank.git
   cd dang-khoa-bank
   ```
2. Cài đặt các thư viện phụ thuộc:
   ```bash
   pip install PyQt6 qrcode pillow
   ```
3. Chạy ứng dụng:
   ```bash
   python src/main.py
   ```

## Định hướng phát triển tương lai
- **Phát hiện gian lận bằng AI:** Tích hợp Machine Learning để phân tích hành vi giao dịch đáng ngờ.
- **Đồng bộ hóa đám mây:** Tùy chọn sao lưu mã hóa lên đám mây để truy cập đa thiết bị.
- **Báo cáo nâng cao:** Hỗ trợ xuất các báo cáo tài chính định dạng PDF và Excel.
- **Ứng dụng di động đồng hành:** App di động phụ trợ để nhận thông báo đẩy tức thời.

## Giấy phép sử dụng
Dự án được phân phối theo **MIT License**.
