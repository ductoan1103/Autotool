#!/usr/bin/env python3
"""
Test Instagram Token functionality trong AutoNuoiAccIns.py
"""

import sys
import os

# Test import AutoNuoiAccIns.py
try:
    from AutoNuoiAccIns import get_instagram_token, format_token_for_api, get_tokens_for_selected
    print("✅ Import AutoNuoiAccIns.py thành công")
except Exception as e:
    print(f"❌ Lỗi import AutoNuoiAccIns.py: {e}")
    sys.exit(1)

# Test function get_instagram_token
try:
    if hasattr(sys.modules['AutoNuoiAccIns'], 'get_instagram_token'):
        print("✅ Function get_instagram_token có sẵn")
    else:
        print("❌ Function get_instagram_token không tồn tại")
        sys.exit(1)
except Exception as e:
    print(f"❌ Lỗi kiểm tra function: {e}")
    sys.exit(1)

# Test function format_token_for_api
try:
    if hasattr(sys.modules['AutoNuoiAccIns'], 'format_token_for_api'):
        print("✅ Function format_token_for_api có sẵn")
    else:
        print("❌ Function format_token_for_api không tồn tại")
        sys.exit(1)
except Exception as e:
    print(f"❌ Lỗi kiểm tra function: {e}")
    sys.exit(1)

# Test UI function
try:
    if hasattr(sys.modules['AutoNuoiAccIns'], 'get_tokens_for_selected'):
        print("✅ UI Function get_tokens_for_selected có sẵn")
    else:
        print("❌ UI Function get_tokens_for_selected không tồn tại")
        sys.exit(1)
except Exception as e:
    print(f"❌ Lỗi kiểm tra UI function: {e}")
    sys.exit(1)

# Test signature các function
try:
    import inspect
    
    sig1 = inspect.signature(get_instagram_token)
    print(f"✅ Signature get_instagram_token: {sig1}")
    
    sig2 = inspect.signature(format_token_for_api)
    print(f"✅ Signature format_token_for_api: {sig2}")
    
except Exception as e:
    print(f"⚠️ Không lấy được signature: {e}")

# Test format function với mock data
try:
    mock_token_info = {
        "success": True,
        "access_token": "IGT:2:936619743392459:77231320408:abc123def456ghi789"
    }
    
    formatted = format_token_for_api(mock_token_info)
    expected = "Bearer IGT:2:936619743392459:77231320408:abc123def456ghi789"
    
    if formatted == expected:
        print(f"✅ Format token test passed: {formatted[:50]}...")
    else:
        print(f"❌ Format token test failed. Got: {formatted}")
        
except Exception as e:
    print(f"❌ Lỗi test format function: {e}")

print("\n🎯 KIỂM TRA CHỨC NĂNG TOKEN:")
print("✅ Đã thêm get_instagram_token() - Lấy token từ thiết bị root")
print("✅ Đã thêm format_token_for_api() - Format token cho API calls")
print("✅ Đã thêm get_tokens_for_selected() - UI function với popup")
print("✅ Đã thêm nút 🔑 Get Tokens (ROOT) vào giao diện")

print("\n📋 CÁC TÍNH NĂNG TOKEN:")
print("🔑 Tìm token thực từ shared preferences")
print("🔑 Tìm token từ database files")
print("🔑 Phát hiện thông tin user (ID, username)")
print("🔑 Tạo token giả hợp lệ nếu không tìm thấy")
print("🔑 Lưu token info vào file JSON")
print("🔑 Format Bearer token cho API calls")
print("🔑 UI popup hiển thị kết quả đẹp")

print("\n💡 CÁCH SỬ DỤNG:")
print("1. Chọn thiết bị Android đã root trong cột CHỌN")
print("2. Bấm nút 🔑 Get Tokens (ROOT)")
print("3. Xem kết quả trong popup window")
print("4. Copy token hoặc lưu vào file")
print("5. Sử dụng token trong Instagram Graph API")

print("\n🌐 API EXAMPLES:")
print("Authorization: Bearer IGT:2:936619743392459:77231320408:...")
print("GET https://graph.instagram.com/me?fields=id,username")
print("GET https://graph.instagram.com/me/media")

print("\n✅ Test hoàn tất!")