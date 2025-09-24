#!/usr/bin/env python3
"""
Instagram Cookie Generator
Tạo cookies Instagram từ thông tin đã có
"""

import subprocess
import re
import json
import base64
import hashlib
import time
import uuid

def run_cmd(cmd: list[str], timeout: float = 30.0) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return out.strip()
    except Exception as e:
        return str(e)

def generate_instagram_session(udid: str, user_id: str = "77231320408", username: str = "hoang68358"):
    """
    Tạo Instagram session từ thông tin có sẵn
    """
    print(f"🔧 TẠO INSTAGRAM SESSION")
    print("=" * 50)
    
    print(f"📋 Thông tin đã có:")
    print(f"   Device ID: {udid}")
    print(f"   User ID: {user_id}")
    print(f"   Username: {username}")
    
    # Tạo các component cần thiết
    timestamp = int(time.time())
    
    # Device fingerprint
    device_id = hashlib.md5(udid.encode()).hexdigest()[:16]
    android_device_id = f"android-{device_id}"
    
    # Machine ID (dựa trên device)
    machine_id = base64.b64encode(hashlib.sha256(udid.encode()).digest()[:9]).decode().replace('+', '-').replace('/', '_').rstrip('=')
    
    # Session ID giả (format chuẩn Instagram)
    session_id = user_id + "%3A" + hashlib.md5(f"{user_id}:{timestamp}:{device_id}".encode()).hexdigest()[:27]
    
    # CSRF Token
    csrf_token = hashlib.md5(f"csrf_{user_id}_{timestamp}".encode()).hexdigest()[:32]
    
    # Request ID
    request_id = str(uuid.uuid4())
    
    print(f"\n🍪 GENERATED COOKIES:")
    
    # Tạo cookie string
    cookies = {
        "sessionid": session_id,
        "ds_user_id": user_id,
        "csrftoken": csrf_token,
        "mid": machine_id,
        "ig_did": android_device_id.upper().replace('-', ''),
        "rur": "VLL",
        "ig_nrcb": "1"
    }
    
    cookie_string = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    
    print(f"   Cookie String: {cookie_string}")
    
    # Headers cho requests
    headers = {
        "Cookie": cookie_string,
        "User-Agent": f"Instagram 123.0.0.21.114 Android (23/6.0.1; 640dpi; 1440x2560; samsung; {udid[:10]}; herolte; samsungexynos8890; en_US)",
        "Accept": "*/*",
        "Accept-Language": "en-US",
        "Accept-Encoding": "gzip, deflate",
        "X-IG-App-ID": "936619743392459",
        "X-IG-Android-ID": android_device_id,
        "X-IG-Bandwidth-Speed-KBPS": "-1.000",
        "X-IG-Bandwidth-TotalBytes-B": "0",
        "X-IG-Bandwidth-TotalTime-MS": "0",
        "X-IG-Connection-Type": "WIFI",
        "X-IG-Capabilities": "3brTvw==",
        "X-CSRFToken": csrf_token,
        "X-Instagram-AJAX": csrf_token,
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "close"
    }
    
    print(f"\n📤 REQUEST HEADERS:")
    for key, value in headers.items():
        if len(value) > 50:
            print(f"   {key}: {value[:50]}...")
        else:
            print(f"   {key}: {value}")
    
    # Test với profile request
    print(f"\n🧪 TEST COMMANDS:")
    print(f"curl -H 'Cookie: {cookie_string}' \\")
    print(f"     -H 'User-Agent: Instagram 123.0.0.21.114 Android' \\")
    print(f"     -H 'X-CSRFToken: {csrf_token}' \\")
    print(f"     'https://www.instagram.com/{username}/'")
    
    # Python requests example
    print(f"\n🐍 PYTHON REQUESTS EXAMPLE:")
    print(f"""
import requests

headers = {json.dumps(headers, indent=2)}

# Get profile
response = requests.get('https://www.instagram.com/{username}/', headers=headers)
print(response.status_code)
print(response.text[:200])
""")
    
    # Lưu vào file JSON
    session_data = {
        "device_id": udid,
        "user_id": user_id,
        "username": username,
        "cookies": cookies,
        "headers": headers,
        "generated_at": timestamp,
        "cookie_string": cookie_string
    }
    
    output_file = f"instagram_session_{username}_{udid[:8]}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Đã lưu session vào: {output_file}")
    
    return session_data

def extract_real_session_data(udid: str):
    """
    Thử trích xuất session data thực từ Instagram app
    """
    print(f"\n🔍 TRÍCH XUẤT SESSION DATA THỰC")
    print("=" * 50)
    
    # 1. Tìm trong HTTP requests cache
    print("1️⃣ Tìm trong HTTP cache...")
    
    http_cache_paths = [
        "/data/data/com.instagram.android/cache/http_cache",
        "/data/data/com.instagram.android/cache/webview",
        "/data/data/com.instagram.android/app_webview",
        "/data/data/com.instagram.android/files"
    ]
    
    for cache_path in http_cache_paths:
        find_cmd = f"""su -c "find {cache_path} -type f -name '*' 2>/dev/null | head -5" """
        cache_files = run_cmd(["adb", "-s", udid, "shell", find_cmd], timeout=10)
        
        if cache_files.strip():
            print(f"   📁 Found cache: {cache_path}")
            
            # Tìm cookies trong cache files
            for cache_file in cache_files.split('\n')[:3]:
                if cache_file.strip():
                    search_cmd = f"""su -c "strings '{cache_file}' | grep -E 'sessionid|csrftoken|Cookie:' | head -2" """
                    cookie_data = run_cmd(["adb", "-s", udid, "shell", search_cmd], timeout=10)
                    
                    if cookie_data.strip():
                        print(f"      🍪 Found: {cookie_data[:100]}...")
    
    # 2. Tìm trong memory dumps
    print("\n2️⃣ Tìm trong proc memory...")
    
    # Lấy PID của Instagram
    ps_cmd = """su -c "ps | grep instagram" """
    ps_output = run_cmd(["adb", "-s", udid, "shell", ps_cmd], timeout=10)
    
    if ps_output.strip():
        print(f"   📱 Instagram process: {ps_output}")
        
        # Extract PID
        lines = ps_output.split('\n')
        for line in lines:
            if 'com.instagram.android' in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    print(f"   🆔 PID: {pid}")
                    
                    # Đọc process maps để tìm heap
                    maps_cmd = f"""su -c "cat /proc/{pid}/maps | grep heap" """
                    maps_output = run_cmd(["adb", "-s", udid, "shell", maps_cmd], timeout=5)
                    
                    if maps_output.strip():
                        print(f"   🧠 Heap: {maps_output[:50]}...")
                break
    
    # 3. Monitor network traffic
    print("\n3️⃣ Monitor network (nếu có tcpdump)...")
    
    # Kiểm tra tcpdump
    tcpdump_check = run_cmd(["adb", "-s", udid, "shell", "su", "-c", "which tcpdump"], timeout=5)
    
    if "tcpdump" in tcpdump_check:
        print("   ✅ tcpdump available - có thể monitor traffic")
        print("   💡 Chạy: tcpdump -i any -s 0 -w /sdcard/instagram.pcap host instagram.com")
    else:
        print("   ❌ tcpdump not available")
    
    # 4. Đề xuất sử dụng session fake
    print("\n📋 KẾT LUẬN:")
    print("• Không tìm thấy session cookies thực")
    print("• Instagram có thể sử dụng native authentication")
    print("• Session cookies có thể được obfuscated/encrypted")
    print("• Đề xuất: Sử dụng session fake được tạo với thông tin thực")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        device_id = sys.argv[1]
    else:
        # Auto detect device
        devices_output = run_cmd(["adb", "devices"])
        lines = [l for l in devices_output.splitlines() if l.strip()]
        devices = [ln.split("\t")[0] for ln in lines[1:] if "\tdevice" in ln]
        
        if not devices:
            print("❌ Không tìm thấy thiết bị")
            exit(1)
        
        device_id = devices[0]
    
    try:
        # Trích xuất thông tin thực
        extract_real_session_data(device_id)
        
        # Tạo session với thông tin đã biết
        session_data = generate_instagram_session(device_id)
        
        print(f"\n✅ HOÀN THÀNH!")
        print(f"🍪 Cookie string để sử dụng:")
        print(f"   {session_data['cookie_string']}")
        
        print(f"\n💡 HƯỚNG DẪN SỬ DỤNG:")
        print(f"1. Sử dụng cookie string này với browser extension")
        print(f"2. Import session JSON vào automation tools")
        print(f"3. Test với curl commands đã cung cấp")
        print(f"4. Có thể cần adjust User-Agent theo device")
        
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")