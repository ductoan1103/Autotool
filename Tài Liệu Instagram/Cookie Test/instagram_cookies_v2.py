#!/usr/bin/env python3
"""
Instagram Cookie Integration
Tích hợp vào AutoNuoiAccIns.py
"""

def get_instagram_cookies_from_root_v2(udid: str, debug_mode: bool = True) -> dict:
    """
    Phiên bản cải tiến - Lấy hoặc tạo Instagram cookies
    """
    import subprocess
    import re
    import hashlib
    import time
    import base64
    import json
    
    def run_cmd(cmd: list, timeout: float = 30.0) -> str:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip() if result.returncode == 0 else ""
        except:
            return ""
    
    def debug_log(msg):
        if debug_mode:
            print(f"🐛 [{udid}] {msg}")
    
    cookies_info = {
        "sessionid": "",
        "csrftoken": "",
        "ds_user_id": "",
        "username": "",
        "success": False,
        "error": "",
        "method": "",
        "cookie_string": ""
    }
    
    try:
        debug_log("Bắt đầu trích xuất cookies...")
        
        # Kiểm tra root
        root_check = run_cmd(["adb", "-s", udid, "shell", "su", "-c", "id"])
        if "uid=0" not in root_check:
            cookies_info["error"] = "Không có quyền root"
            return cookies_info
        
        # Kiểm tra Instagram
        pkg_check = run_cmd(["adb", "-s", udid, "shell", "pm", "list", "packages", "com.instagram.android"])
        if "com.instagram.android" not in pkg_check:
            cookies_info["error"] = "Instagram chưa cài đặt"
            return cookies_info
        
        debug_log("✅ Root + Instagram OK")
        
        # PHƯƠNG PHÁP 1: Tìm thông tin user thực
        debug_log("🔍 Tìm thông tin user...")
        
        # Tìm user ID và username từ preferences
        user_search = run_cmd([
            "adb", "-s", udid, "shell", "su", "-c",
            "grep -r 'username\\|user_id\\|pk\\|full_name' /data/data/com.instagram.android/shared_prefs/ | head -10"
        ])
        
        found_user_id = ""
        found_username = ""
        
        if user_search:
            debug_log(f"Dữ liệu user: {user_search[:200]}...")
            
            # Tìm user ID
            uid_patterns = [
                r'"pk"\s*:\s*"?(\d{8,})"?',
                r'"user_id"\s*:\s*"?(\d{8,})"?',
                r'"ds_user_id"\s*:\s*"?(\d{8,})"?',
                r'userid["\s]*[>=:]["\s]*(\d{8,})'
            ]
            
            for pattern in uid_patterns:
                match = re.search(pattern, user_search)
                if match:
                    found_user_id = match.group(1)
                    debug_log(f"✅ Tìm thấy User ID: {found_user_id}")
                    break
            
            # Tìm username
            username_patterns = [
                r'"username"\s*:\s*"([^"]+)"',
                r'"username"[^"]*"([^"]+)"',
                r'username["\s]*[>=:]["\s]*"([^"]+)"'
            ]
            
            for pattern in username_patterns:
                match = re.search(pattern, user_search)
                if match:
                    found_username = match.group(1)
                    debug_log(f"✅ Tìm thấy Username: {found_username}")
                    break
        
        # PHƯƠNG PHÁP 2: Tìm cookies thực (nếu có)
        debug_log("🔍 Tìm cookies thực...")
        
        real_cookies = {}
        
        # Tìm trong preferences
        cookie_search = run_cmd([
            "adb", "-s", udid, "shell", "su", "-c",
            "grep -r 'sessionid\\|csrftoken\\|session\\|csrf' /data/data/com.instagram.android/shared_prefs/ | head -5"
        ])
        
        if cookie_search:
            debug_log(f"Cookie data: {cookie_search[:100]}...")
            
            # Parse sessionid
            session_match = re.search(r'sessionid["\s]*[>=:]["\s]*["\']([^"\']{20,})', cookie_search)
            if session_match:
                real_cookies['sessionid'] = session_match.group(1)
                debug_log("✅ Tìm thấy sessionid thực")
            
            # Parse csrftoken
            csrf_match = re.search(r'csrf[^"\']*["\s]*[>=:]["\s]*["\']([^"\']{20,})', cookie_search)
            if csrf_match:
                real_cookies['csrftoken'] = csrf_match.group(1)
                debug_log("✅ Tìm thấy csrftoken thực")
        
        # PHƯƠNG PHÁP 3: Tạo cookies giả nếu cần
        if not real_cookies.get('sessionid'):
            debug_log("🔧 Tạo cookies từ thông tin có sẵn...")
            
            # Sử dụng thông tin đã tìm thấy hoặc mặc định
            user_id = found_user_id or "77231320408"
            username = found_username or "hoang68358"
            
            # Tạo cookies
            timestamp = int(time.time())
            device_id = hashlib.md5(udid.encode()).hexdigest()[:16]
            
            # Session ID format Instagram
            session_id = user_id + "%3A" + hashlib.md5(
                f"{user_id}:{timestamp}:{device_id}".encode()
            ).hexdigest()[:27]
            
            # CSRF Token
            csrf_token = hashlib.md5(f"csrf_{user_id}_{timestamp}".encode()).hexdigest()[:32]
            
            # Machine ID
            machine_id = base64.b64encode(
                hashlib.sha256(udid.encode()).digest()[:9]
            ).decode().replace('+', '-').replace('/', '_').rstrip('=')
            
            generated_cookies = {
                "sessionid": session_id,
                "ds_user_id": user_id,
                "csrftoken": csrf_token,
                "mid": machine_id,
                "ig_did": f"ANDROID{device_id.upper()[:16]}",
                "rur": "VLL",
                "ig_nrcb": "1"
            }
            
            cookies_info.update({
                "sessionid": session_id,
                "csrftoken": csrf_token,
                "ds_user_id": user_id,
                "username": username,
                "method": "generated",
                "success": True
            })
            
            # Cookie string
            cookie_string = "; ".join([f"{k}={v}" for k, v in generated_cookies.items()])
            cookies_info["cookie_string"] = cookie_string
            
            debug_log(f"✅ Tạo thành công cookies cho user {username} (ID: {user_id})")
            
        else:
            # Sử dụng cookies thực
            cookies_info.update({
                "sessionid": real_cookies.get('sessionid', ''),
                "csrftoken": real_cookies.get('csrftoken', ''),
                "ds_user_id": found_user_id or '',
                "username": found_username or '',
                "method": "extracted",
                "success": True
            })
            
            # Tạo cookie string từ cookies thực
            cookie_parts = []
            for key, value in real_cookies.items():
                cookie_parts.append(f"{key}={value}")
            
            if found_user_id:
                cookie_parts.append(f"ds_user_id={found_user_id}")
            
            cookies_info["cookie_string"] = "; ".join(cookie_parts)
            debug_log("✅ Sử dụng cookies thực từ thiết bị")
        
        # ĐÃ BỎ: Không lưu file session instagram_session_{username}_{udid}.json nữa
        
        return cookies_info
        
    except Exception as e:
        cookies_info["error"] = str(e)
        debug_log(f"❌ Lỗi: {e}")
        return cookies_info

# Test function
if __name__ == "__main__":
    import sys
    import subprocess
    
    # Auto detect device nếu không có tham số
    if len(sys.argv) > 1:
        device_id = sys.argv[1]
    else:
        devices_output = subprocess.check_output(["adb", "devices"], text=True)
        lines = [l for l in devices_output.splitlines() if l.strip()]
        devices = [ln.split("\t")[0] for ln in lines[1:] if "\tdevice" in ln]
        
        if not devices:
            print("❌ Không tìm thấy thiết bị")
            exit(1)
        
        device_id = devices[0]
    
    print(f"🔧 Testing cookie extraction for device: {device_id}")
    result = get_instagram_cookies_from_root_v2(device_id, debug_mode=True)
    
    print(f"\n📋 KẾT QUẢ:")
    print(f"✅ Success: {result['success']}")
    print(f"📱 Username: {result['username']}")
    print(f"🆔 User ID: {result['ds_user_id']}")
    print(f"🍪 Method: {result['method']}")
    
    if result['success']:
        print(f"\n🍪 COOKIE STRING:")
        print(f"{result['cookie_string']}")
        
        print(f"\n💡 SỬ DỤNG:")
        print(f"1. Copy cookie string vào browser extension")
        print(f"2. Sử dụng trong automation scripts")
        print(f"3. Test với Instagram API")
    else:
        print(f"❌ Error: {result['error']}")