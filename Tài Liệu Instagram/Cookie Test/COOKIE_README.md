# Instagram Cookie Extractor - Hướng dẫn sử dụng

## Tính năng mới: Lấy Cookie từ máy Root

### Yêu cầu hệ thống:

1. **Thiết bị Android đã Root** với quyền su
2. **Instagram app** đã cài đặt và đăng nhập
3. **ADB** được cài đặt và thiết bị kết nối qua USB
4. **USB Debugging** được bật

### Cách sử dụng:

1. **Kết nối thiết bị:**

   - Kết nối thiết bị Android root qua USB
   - Bật USB Debugging
   - Chấp nhận yêu cầu USB Debugging từ máy tính

2. **Chạy ứng dụng:**

   ```bash
   python AutoNuoiAccIns.py
   ```

3. **Lấy cookies:**
   - Bấm nút **"Refresh thiết bị"** để phát hiện thiết bị
   - **Tick chọn** thiết bị ở cột "CHỌN"
   - Bấm nút **"🍪 Get Cookies (ROOT)"**

### Quy trình hoạt động:

1. **Kiểm tra Root:** Xác minh thiết bị có quyền root
2. **Kiểm tra Instagram:** Đảm bảo app đã cài đặt
3. **Truy cập dữ liệu:** Đọc từ `/data/data/com.instagram.android/`
4. **Tìm kiếm cookies:**
   - Tìm trong `shared_prefs/*.xml`
   - Tìm trong WebView cookies database
5. **Hiển thị kết quả:** Popup window với cookies và username

### Dữ liệu thu được:

- **sessionid:** Cookie phiên đăng nhập chính
- **csrftoken:** Token bảo mật CSRF
- **ds_user_id:** ID người dùng Instagram
- **username:** Tên đăng nhập

### Format kết quả:

```
Username: your_username
Cookies: sessionid=ABC123...; csrftoken=XYZ789...; ds_user_id=123456789
```

### Xử lý lỗi thường gặp:

1. **"Thiết bị không có quyền root"**

   - Đảm bảo thiết bị đã root
   - Cấp quyền su khi được yêu cầu

2. **"Instagram app chưa được cài đặt"**

   - Cài đặt Instagram từ Play Store
   - Đăng nhập vào tài khoản

3. **"Không tìm thấy session cookies"**
   - Đảm bảo đã đăng nhập Instagram
   - Thử mở Instagram và đăng nhập lại
   - Khởi động lại thiết bị

### Bảo mật:

⚠️ **Cảnh báo:** Cookies này có thể truy cập vào tài khoản Instagram của bạn. Hãy:

- Không chia sẻ với người khác
- Sử dụng cho mục đích cá nhân hoặc test
- Thường xuyên đổi mật khẩu Instagram

### Test script:

Sử dụng file `test_cookies.py` để kiểm tra tính năng:

```bash
python test_cookies.py
```

Script này sẽ kiểm tra:

- Kết nối ADB
- Quyền root
- Instagram app
- Khả năng truy cập dữ liệu

### Tính năng nâng cao:

- **Copy to Clipboard:** Sao chép cookies vào clipboard
- **Multi-device:** Hỗ trợ nhiều thiết bị cùng lúc
- **Detailed logging:** Ghi log chi tiết quá trình

---

**Phát triển bởi:** Auto Instagram Tool
**Phiên bản:** 1.0
**Ngày cập nhật:** $(date +%d/%m/%Y)
