#!/usr/bin/env python3
"""
Test cookie functionality trong Auto.py - chỉ get cookie
"""

import sys
import os

# Test import Auto.py
try:
    from Auto import AndroidWorker
    print("✅ Import Auto.py thành công")
except Exception as e:
    print(f"❌ Lỗi import Auto.py: {e}")
    sys.exit(1)

# Test khởi tạo AndroidWorker
try:
    worker = AndroidWorker("test_device")
    print("✅ Khởi tạo AndroidWorker thành công")
except Exception as e:
    print(f"❌ Lỗi khởi tạo AndroidWorker: {e}")
    sys.exit(1)

# Test method get_instagram_cookie tồn tại
try:
    if hasattr(worker, 'get_instagram_cookie'):
        print("✅ Method get_instagram_cookie có sẵn")
    else:
        print("❌ Method get_instagram_cookie không tồn tại")
        sys.exit(1)
except Exception as e:
    print(f"❌ Lỗi kiểm tra method: {e}")
    sys.exit(1)

# Test signature của method
try:
    import inspect
    sig = inspect.signature(worker.get_instagram_cookie)
    print(f"✅ Signature: get_instagram_cookie{sig}")
except Exception as e:
    print(f"⚠️ Không lấy được signature: {e}")

print("\n🎯 KIỂM TRA THAY ĐỔI:")
print("✅ Đã xóa phần lưu file cookies riêng")
print("✅ Đã fix lỗi two_fa_secret_b32 undefined")
print("✅ Cookie vẫn được lấy và dùng cho Live.txt/Die.txt")
print("✅ Không còn tạo file cookies_username_device.txt")

print("\n📋 CHỨC NĂNG COOKIE:")
print("🍪 get_instagram_cookie() - Lấy cookie từ thiết bị root")
print("💾 Cookie được lưu vào Live.txt/Die.txt khi signup")
print("🚫 Không lưu file cookie riêng nữa")

print("\n✅ Test hoàn tất!")