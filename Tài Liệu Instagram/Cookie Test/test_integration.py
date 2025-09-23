#!/usr/bin/env python3
"""
Test AutoNuoiAccIns.py Integration
Kiểm tra function cookie đã tích hợp vào AutoNuoiAccIns.py chưa
"""

import sys
import os

# Add path để import AutoNuoiAccIns
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import function từ AutoNuoiAccIns.py
    from AutoNuoiAccIns import get_instagram_cookies_v2
    
    print("✅ Import thành công get_instagram_cookies_v2 từ AutoNuoiAccIns.py")
    
    # Test với device ID
    device_id = "33008a430e2ca375"
    print(f"🔧 Testing với device: {device_id}")
    
    # Gọi function
    result = get_instagram_cookies_v2(device_id, debug_mode=True)
    
    print(f"\n📋 KẾT QUẢ:")
    print(f"✅ Success: {result.get('success', False)}")
    print(f"👤 Username: {result.get('username', 'N/A')}")
    print(f"🆔 User ID: {result.get('ds_user_id', 'N/A')}")
    print(f"🔧 Method: {result.get('method', 'N/A')}")
    
    if result.get('success'):
        cookie_string = result.get('cookie_string', '')
        print(f"\n🍪 COOKIE STRING:")
        print(f"{cookie_string[:100]}...")
        
        print(f"\n✅ TÍCH HỢP THÀNH CÔNG!")
        print(f"🎯 Bạn có thể sử dụng:")
        print(f"   1. Mở AutoNuoiAccIns.py")
        print(f"   2. Tick chọn thiết bị")
        print(f"   3. Click '🍪 Get Cookies (ROOT)'")
        print(f"   4. Nhận cookies từ popup")
    else:
        error = result.get('error', 'Unknown error')
        print(f"\n❌ Error: {error}")
        
        if 'root' in error.lower():
            print(f"💡 Cần đảm bảo thiết bị đã root và cấp quyền su")
        elif 'instagram' in error.lower():
            print(f"💡 Cần cài đặt và đăng nhập Instagram trên thiết bị")
    
except ImportError as e:
    print(f"❌ Lỗi import: {e}")
    print(f"💡 Đảm bảo AutoNuoiAccIns.py có function get_instagram_cookies_v2")
    
except Exception as e:
    print(f"❌ Lỗi: {e}")

print(f"\n📂 FILE LOCATIONS:")
print(f"   • AutoNuoiAccIns.py: {os.path.abspath('AutoNuoiAccIns.py')}")
print(f"   • Function: get_instagram_cookies_v2()")
print(f"   • UI Button: '🍪 Get Cookies (ROOT)'")
print(f"   • Command: get_cookies_for_selected()")