#!/usr/bin/env python3
"""
Instagram Token Extractor
Trích xuất và phân tích tokens từ preferences files
"""

import subprocess
import re
import json
import base64
import urllib.parse

def run_cmd(cmd: list[str], timeout: float = 30.0) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return out.strip()
    except Exception as e:
        return str(e)

def decode_base64_safe(data: str) -> str:
    """Safely decode base64 data"""
    try:
        # Thêm padding nếu cần
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        
        decoded = base64.b64decode(data)
        return decoded.decode('utf-8', errors='ignore')
    except:
        return "Unable to decode"

def analyze_tokens_in_preferences(udid: str):
    """Phân tích tokens trong file preferences chính"""
    print(f"🔍 TRÍCH XUẤT TOKENS TỪ PREFERENCES: {udid}")
    print("=" * 60)
    
    prefs_path = "/data/data/com.instagram.android/shared_prefs"
    main_prefs = "com.instagram.android_preferences.xml"
    
    # Đọc file preferences chính
    read_cmd = f"""su -c "cat {prefs_path}/{main_prefs}" """
    file_content = run_cmd(["adb", "-s", udid, "shell", read_cmd], timeout=15)
    
    if len(file_content) < 100:
        print("❌ Không thể đọc file preferences")
        return
    
    print(f"✅ Đọc được file preferences ({len(file_content)} chars)")
    
    # 1. Tìm user_id
    user_id_pattern = r'"user_id"[^"]*"(\d{8,})"'
    user_ids = re.findall(user_id_pattern, file_content)
    
    if user_ids:
        print(f"\n👤 USER IDs tìm thấy:")
        for uid in set(user_ids):
            print(f"   🆔 {uid}")
    
    # 2. Tìm và phân tích các JWT tokens
    jwt_pattern = r'(eyJ[A-Za-z0-9+/=]+)'
    jwt_tokens = re.findall(jwt_pattern, file_content)
    
    if jwt_tokens:
        print(f"\n🎫 JWT TOKENS ({len(jwt_tokens)} found):")
        for i, token in enumerate(jwt_tokens[:5]):  # Chỉ hiển thị 5 cái đầu
            print(f"\n   Token #{i+1}: {token[:30]}...")
            
            # Thử decode JWT header
            try:
                parts = token.split('.')
                if len(parts) >= 2:
                    header_decoded = decode_base64_safe(parts[0])
                    payload_decoded = decode_base64_safe(parts[1])
                    
                    print(f"      Header: {header_decoded}")
                    if len(payload_decoded) < 500:  # Chỉ hiển thị payload ngắn
                        print(f"      Payload: {payload_decoded}")
                    else:
                        print(f"      Payload: {payload_decoded[:100]}...")
            except:
                print("      Unable to decode JWT")
    
    # 3. Tìm các chuỗi dài có thể là session tokens
    long_tokens = re.findall(r'[A-Za-z0-9+/=]{40,}', file_content)
    long_tokens = [t for t in set(long_tokens) if not t.startswith('eyJ')]  # Loại bỏ JWT
    
    if long_tokens:
        print(f"\n🔑 LONG TOKENS ({len(long_tokens)} found):")
        for i, token in enumerate(long_tokens[:10]):
            print(f"   #{i+1}: {token[:40]}...")
            
            # Thử decode nếu có thể
            decoded = decode_base64_safe(token)
            if len(decoded) > 10 and decoded != "Unable to decode":
                print(f"        Decoded: {decoded[:100]}...")
    
    # 4. Tìm authorization headers
    auth_patterns = [
        r'"authorization"[^"]*"([^"]+)"',
        r'"auth_token"[^"]*"([^"]+)"',
        r'"access_token"[^"]*"([^"]+)"',
        r'Bearer\s+([A-Za-z0-9+/=]+)',
        r'"sessionid"[^"]*"([^"]+)"',
        r'"csrftoken"[^"]*"([^"]+)"'
    ]
    
    auth_tokens = []
    for pattern in auth_patterns:
        matches = re.findall(pattern, file_content, re.IGNORECASE)
        for match in matches:
            if len(match) > 10:
                auth_tokens.append((pattern.split('"')[1], match))
    
    if auth_tokens:
        print(f"\n🔐 AUTHORIZATION TOKENS:")
        for token_type, token_value in auth_tokens:
            print(f"   {token_type}: {token_value[:40]}...")
    
    # 5. Tìm JSON structures có chứa session info
    json_pattern = r'\{[^}]*(?:session|token|auth|user)[^}]*\}'
    json_matches = re.findall(json_pattern, file_content, re.IGNORECASE)
    
    if json_matches:
        print(f"\n📊 JSON WITH SESSION DATA:")
        for i, json_str in enumerate(json_matches[:5]):
            # Decode HTML entities
            json_clean = json_str.replace('&quot;', '"').replace('&gt;', '>').replace('&lt;', '<')
            print(f"   JSON #{i+1}: {json_clean[:100]}...")
            
            # Thử parse JSON
            try:
                parsed = json.loads(json_clean)
                for key, value in parsed.items():
                    if any(keyword in key.lower() for keyword in ['session', 'token', 'auth', 'user', 'id']):
                        print(f"      {key}: {str(value)[:50]}...")
            except:
                pass

def extract_chrome_cookies(udid: str):
    """Thử lấy cookies từ Chrome browser"""
    print(f"\n🌐 TRÍCH XUẤT CHROME COOKIES: {udid}")
    print("=" * 60)
    
    chrome_paths = [
        "/data/data/com.android.chrome/app_chrome/Default/Cookies",
        "/data/data/com.chrome.beta/app_chrome/Default/Cookies",
        "/data/data/com.chrome.dev/app_chrome/Default/Cookies"
    ]
    
    for chrome_path in chrome_paths:
        exists = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"test -f {chrome_path} && echo 'exists' || echo 'not found'"], timeout=5)
        
        if "exists" in exists:
            print(f"✅ Found Chrome cookies: {chrome_path}")
            
            # Copy và phân tích
            temp_path = "/sdcard/chrome_cookies.db"
            copy_cmd = f"""su -c "cp '{chrome_path}' {temp_path} && chmod 644 {temp_path}" """
            run_cmd(["adb", "-s", udid, "shell", copy_cmd], timeout=10)
            
            # Query Instagram cookies
            instagram_cookies_cmd = f"""su -c "sqlite3 {temp_path} 'SELECT name, value, host_key FROM cookies WHERE host_key LIKE \"%instagram%\" OR host_key LIKE \"%facebook%\";'" """
            instagram_cookies = run_cmd(["adb", "-s", udid, "shell", instagram_cookies_cmd], timeout=15)
            
            if instagram_cookies.strip():
                print(f"🍪 Instagram cookies in Chrome:")
                lines = instagram_cookies.split('\n')
                for line in lines[:10]:  # Giới hạn 10 dòng
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            name, value, domain = parts[0], parts[1], parts[2]
                            if any(keyword in name.lower() for keyword in ['session', 'csrf', 'token', 'auth']):
                                print(f"   🔑 {name}: {value[:30]}... (domain: {domain})")
            else:
                print("   ❌ Không tìm thấy Instagram cookies")
            
            # Cleanup
            run_cmd(["adb", "-s", udid, "shell", "rm", "-f", temp_path], timeout=5)
        else:
            print(f"❌ Chrome cookies not found: {chrome_path}")

def create_session_from_data(udid: str):
    """Tạo session data từ thông tin đã tìm được"""
    print(f"\n🔧 TẠO SESSION DATA: {udid}")
    print("=" * 60)
    
    # Đọc lại file preferences để lấy thông tin cần thiết
    prefs_path = "/data/data/com.instagram.android/shared_prefs"
    main_prefs = "com.instagram.android_preferences.xml"
    
    read_cmd = f"""su -c "cat {prefs_path}/{main_prefs}" """
    file_content = run_cmd(["adb", "-s", udid, "shell", read_cmd], timeout=15)
    
    session_data = {
        "device_id": udid,
        "user_id": "",
        "username": "",
        "tokens": [],
        "possible_sessionid": "",
        "csrf_token": "",
        "auth_headers": []
    }
    
    # Extract user_id
    user_id_matches = re.findall(r'"user_id"[^"]*"(\d{8,})"', file_content)
    if user_id_matches:
        session_data["user_id"] = user_id_matches[0]
    
    # Extract username
    username_matches = re.findall(r'"username"[^"]*"([a-zA-Z0-9._]+)"', file_content)
    if username_matches:
        session_data["username"] = username_matches[0]
    
    # Extract tokens
    jwt_tokens = re.findall(r'(eyJ[A-Za-z0-9+/=]+)', file_content)
    session_data["tokens"] = jwt_tokens[:5]  # Lấy tối đa 5 tokens
    
    # Tìm possible session data
    session_patterns = [
        r'"sessionid"[^"]*"([^"]+)"',
        r'"session"[^"]*"([^"]+)"',
        r'"ig_session"[^"]*"([^"]+)"'
    ]
    
    for pattern in session_patterns:
        matches = re.findall(pattern, file_content, re.IGNORECASE)
        if matches and len(matches[0]) > 15:
            session_data["possible_sessionid"] = matches[0]
            break
    
    # CSRF token
    csrf_matches = re.findall(r'"csrftoken"[^"]*"([^"]+)"', file_content, re.IGNORECASE)
    if csrf_matches:
        session_data["csrf_token"] = csrf_matches[0]
    
    # Generate report
    print("📋 SESSION DATA SUMMARY:")
    print(f"   Device ID: {session_data['device_id']}")
    print(f"   User ID: {session_data['user_id'] or 'Not found'}")
    print(f"   Username: {session_data['username'] or 'Not found'}")
    print(f"   JWT Tokens: {len(session_data['tokens'])} found")
    print(f"   Session ID: {'Found' if session_data['possible_sessionid'] else 'Not found'}")
    print(f"   CSRF Token: {'Found' if session_data['csrf_token'] else 'Not found'}")
    
    # Tạo cookie string cho browser/requests
    if session_data['user_id']:
        cookie_parts = []
        
        if session_data['possible_sessionid']:
            cookie_parts.append(f"sessionid={session_data['possible_sessionid']}")
        
        if session_data['csrf_token']:
            cookie_parts.append(f"csrftoken={session_data['csrf_token']}")
        
        if session_data['user_id']:
            cookie_parts.append(f"ds_user_id={session_data['user_id']}")
        
        if cookie_parts:
            cookie_string = "; ".join(cookie_parts)
            print(f"\n🍪 GENERATED COOKIE STRING:")
            print(f"   {cookie_string}")
            
            # Tạo headers cho requests
            print(f"\n📤 REQUEST HEADERS:")
            print(f"   Cookie: {cookie_string}")
            print(f"   User-Agent: Instagram 123.0.0.21.114 Android")
            if session_data['csrf_token']:
                print(f"   X-CSRFToken: {session_data['csrf_token']}")
            
            return cookie_string
    
    return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        device_id = sys.argv[1]
    else:
        devices_output = run_cmd(["adb", "devices"])
        lines = [l for l in devices_output.splitlines() if l.strip()]
        devices = [ln.split("\t")[0] for ln in lines[1:] if "\tdevice" in ln]
        
        if not devices:
            print("❌ Không tìm thấy thiết bị")
            exit(1)
        
        device_id = devices[0]
    
    try:
        analyze_tokens_in_preferences(device_id)
        extract_chrome_cookies(device_id)
        cookie_result = create_session_from_data(device_id)
        
        if cookie_result:
            print(f"\n✅ SUCCESS: Đã tạo được cookie string!")
            print(f"📋 Copy cookie này để sử dụng:")
            print(f"   {cookie_result}")
        else:
            print(f"\n⚠️ Không thể tạo được cookie string hoàn chỉnh")
            print(f"💡 Thử đăng nhập lại Instagram và chạy script này")
            
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")