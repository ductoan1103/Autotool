#!/usr/bin/env python3
"""
Instagram Session Builder
Xây dựng session từ JWT tokens và JSON data có sẵn
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

def decode_base64_safe(data: str) -> dict:
    """Safely decode base64 JWT data"""
    try:
        # Thêm padding nếu cần
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        
        decoded = base64.b64decode(data)
        decoded_str = decoded.decode('utf-8', errors='ignore')
        
        # Thử parse JSON
        try:
            return json.loads(decoded_str)
        except:
            return {"raw": decoded_str}
    except:
        return {"error": "Unable to decode"}

def extract_instagram_session_data(udid: str):
    """Trích xuất dữ liệu session Instagram chi tiết"""
    print(f"🔍 TRÍCH XUẤT SESSION DATA CHI TIẾT: {udid}")
    print("=" * 70)
    
    prefs_path = "/data/data/com.instagram.android/shared_prefs"
    main_prefs = "com.instagram.android_preferences.xml"
    
    # Đọc file preferences
    read_cmd = f"""su -c "cat {prefs_path}/{main_prefs}" """
    file_content = run_cmd(["adb", "-s", udid, "shell", read_cmd], timeout=15)
    
    if len(file_content) < 100:
        print("❌ Không thể đọc file preferences")
        return None
    
    session_info = {
        "user_id": "",
        "username": "",
        "sessionid": "",
        "csrf_token": "",
        "authorization": "",
        "device_id": udid,
        "jwt_tokens": [],
        "auth_headers": {}
    }
    
    print("🔍 1. Phân tích JWT Tokens...")
    # Tìm và decode JWT tokens
    jwt_pattern = r'(eyJ[A-Za-z0-9+/=]+\.eyJ[A-Za-z0-9+/=]+(?:\.[A-Za-z0-9+/=]+)?)'
    jwt_tokens = re.findall(jwt_pattern, file_content)
    
    for i, token in enumerate(jwt_tokens):
        try:
            parts = token.split('.')
            if len(parts) >= 2:
                header = decode_base64_safe(parts[0])
                payload = decode_base64_safe(parts[1])
                
                print(f"   JWT #{i+1}:")
                print(f"      Header: {header}")
                print(f"      Payload: {json.dumps(payload, indent=8)[:200]}...")
                
                # Tìm thông tin hữu ích trong payload
                if isinstance(payload, dict):
                    if 'user_id' in payload:
                        session_info['user_id'] = str(payload['user_id'])
                    if 'username' in payload:
                        session_info['username'] = payload['username']
                    if 'sessionid' in payload:
                        session_info['sessionid'] = payload['sessionid']
                
                session_info['jwt_tokens'].append({
                    'token': token,
                    'header': header,
                    'payload': payload
                })
        except Exception as e:
            print(f"   JWT #{i+1}: Error decoding - {e}")
    
    print("\n🔍 2. Phân tích JSON Structures...")
    # Tìm JSON chứa thông tin user
    json_pattern = r'\{[^}]*(?:user_id|username|session)[^}]*\}'
    json_matches = re.findall(json_pattern, file_content, re.IGNORECASE)
    
    for i, json_str in enumerate(json_matches):
        try:
            # Clean up HTML entities
            json_clean = json_str.replace('&quot;', '"').replace('&gt;', '>').replace('&lt;', '<').replace('\\"', '"')
            
            # Thử parse JSON
            parsed = json.loads(json_clean)
            
            print(f"   JSON #{i+1}: {json.dumps(parsed, indent=6)[:200]}...")
            
            # Extract useful info
            if isinstance(parsed, dict):
                for key, value in parsed.items():
                    if key == 'user_id' or (isinstance(value, str) and value.isdigit() and len(value) > 8):
                        session_info['user_id'] = str(value)
                    elif key == 'username' and isinstance(value, str) and len(value) > 2:
                        session_info['username'] = value
                    elif 'session' in key.lower() and isinstance(value, str) and len(value) > 10:
                        session_info['sessionid'] = value
                    
                    # Nếu value là string chứa JSON, thử parse tiếp
                    if isinstance(value, str) and value.startswith('{'):
                        try:
                            nested = json.loads(value)
                            if isinstance(nested, dict):
                                if 'user_id' in nested:
                                    session_info['user_id'] = str(nested['user_id'])
                                if 'username' in nested:
                                    session_info['username'] = nested['username']
                        except:
                            pass
                            
        except Exception as e:
            continue
    
    print("\n🔍 3. Tìm kiếm Authorization Headers...")
    # Tìm authorization patterns
    auth_patterns = [
        (r'"Authorization"[^"]*"([^"]+)"', 'Authorization'),
        (r'"auth[^"]*"[^"]*"([^"]+)"', 'Auth Token'),
        (r'"x-ig-app-id"[^"]*"([^"]+)"', 'App ID'),
        (r'"x-instagram-ajax"[^"]*"([^"]+)"', 'AJAX Token'),
        (r'"sessionid"[^"]*"([^"]+)"', 'Session ID'),
        (r'"csrftoken"[^"]*"([^"]+)"', 'CSRF Token'),
        (r'Bearer\s+([A-Za-z0-9+/=]+)', 'Bearer Token')
    ]
    
    for pattern, name in auth_patterns:
        matches = re.findall(pattern, file_content, re.IGNORECASE)
        for match in matches:
            if len(match) > 10:
                session_info['auth_headers'][name] = match
                print(f"   {name}: {match[:30]}...")
                
                # Special handling for specific tokens
                if name == 'Session ID':
                    session_info['sessionid'] = match
                elif name == 'CSRF Token':
                    session_info['csrf_token'] = match
                elif name == 'Authorization' or name == 'Bearer Token':
                    session_info['authorization'] = match
    
    print("\n🔍 4. Tìm trong các file khác...")
    # Kiểm tra file USER_PREFERENCES
    user_prefs = "77231320408_USER_PREFERENCES.xml"
    user_cmd = f"""su -c "cat {prefs_path}/{user_prefs}" """
    user_content = run_cmd(["adb", "-s", udid, "shell", user_cmd], timeout=10)
    
    if len(user_content) > 100:
        # Tìm thông tin trong user preferences
        user_id_matches = re.findall(r'"user_id"[^"]*"(\d{8,})"', user_content)
        if user_id_matches and not session_info['user_id']:
            session_info['user_id'] = user_id_matches[0]
            print(f"   User ID từ USER_PREFERENCES: {session_info['user_id']}")
    
    return session_info

def build_instagram_session(session_info: dict):
    """Xây dựng session Instagram từ thông tin đã trích xuất"""
    print(f"\n🔧 XÂY DỰNG INSTAGRAM SESSION")
    print("=" * 50)
    
    if not session_info:
        print("❌ Không có thông tin session")
        return None
    
    print("📋 THÔNG TIN SESSION:")
    print(f"   Device ID: {session_info['device_id']}")
    print(f"   User ID: {session_info['user_id'] or 'Chưa tìm thấy'}")
    print(f"   Username: {session_info['username'] or 'Chưa tìm thấy'}")
    print(f"   JWT Tokens: {len(session_info['jwt_tokens'])}")
    print(f"   Session ID: {'✅' if session_info['sessionid'] else '❌'}")
    print(f"   CSRF Token: {'✅' if session_info['csrf_token'] else '❌'}")
    print(f"   Authorization: {'✅' if session_info['authorization'] else '❌'}")
    
    # Tạo cookie string
    cookie_parts = []
    
    if session_info['sessionid']:
        cookie_parts.append(f"sessionid={session_info['sessionid']}")
    
    if session_info['csrf_token']:
        cookie_parts.append(f"csrftoken={session_info['csrf_token']}")
    
    if session_info['user_id']:
        cookie_parts.append(f"ds_user_id={session_info['user_id']}")
    
    # Thêm một số cookies cơ bản của Instagram
    cookie_parts.extend([
        f"mid=ZEK-jQALAAF7U1OI3W4lNc25_ct9",  # Machine ID (có thể fake)
        f"ig_did=B2E8DA3A-F8A6-4B8E-9AB2-123456789ABC",  # Device ID
        f"rur=VLL"  # Region
    ])
    
    if cookie_parts:
        cookie_string = "; ".join(cookie_parts)
        
        print(f"\n🍪 COOKIE STRING:")
        print(f"   {cookie_string}")
        
        # Tạo headers cho requests
        headers = {
            "Cookie": cookie_string,
            "User-Agent": "Instagram 123.0.0.21.114 Android (23/6.0.1; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US)",
            "Accept": "*/*",
            "Accept-Language": "en-US",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close"
        }
        
        if session_info['csrf_token']:
            headers["X-CSRFToken"] = session_info['csrf_token']
        
        if session_info['authorization']:
            headers["Authorization"] = session_info['authorization']
        
        # Thêm Instagram-specific headers
        headers.update({
            "X-IG-App-ID": "936619743392459",
            "X-IG-WWW-Claim": "0",
            "X-Requested-With": "XMLHttpRequest"
        })
        
        print(f"\n📤 REQUEST HEADERS:")
        for key, value in headers.items():
            if len(value) > 50:
                print(f"   {key}: {value[:50]}...")
            else:
                print(f"   {key}: {value}")
        
        # Test cookie với một request đơn giản
        print(f"\n🧪 TEST SESSION:")
        print(f"   Để test session này, thử:")
        print(f"   curl -H 'Cookie: {cookie_string}' https://www.instagram.com/accounts/edit/")
        
        return {
            'cookies': cookie_string,
            'headers': headers,
            'session_info': session_info
        }
    
    else:
        print(f"\n❌ Không đủ thông tin để tạo session")
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
        session_info = extract_instagram_session_data(device_id)
        
        if session_info:
            session_result = build_instagram_session(session_info)
            
            if session_result:
                print(f"\n✅ SUCCESS: Đã xây dựng được Instagram session!")
                
                # Lưu kết quả vào file
                output_file = f"instagram_session_{device_id}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(session_result, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Đã lưu session vào file: {output_file}")
                print(f"📋 Cookie string: {session_result['cookies']}")
            else:
                print(f"\n⚠️ Không thể xây dựng session hoàn chỉnh")
        else:
            print(f"\n❌ Không thể trích xuất session data")
            
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")