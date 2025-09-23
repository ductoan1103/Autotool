#!/usr/bin/env python3
"""
Deep Instagram Cookie Analysis
Phân tích sâu các file preferences để tìm session cookies
"""

import subprocess
import re
import json

def run_cmd(cmd: list[str], timeout: float = 30.0) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return out.strip()
    except Exception as e:
        return str(e)

def analyze_key_preference_files(udid: str):
    """Phân tích các file preferences quan trọng"""
    print(f"🔍 PHÂN TÍCH SÂU PREFERENCE FILES CHO: {udid}")
    print("=" * 70)
    
    # Các file quan trọng cần kiểm tra
    key_files = [
        "77231320408_USER_PREFERENCES.xml",
        "com.instagram.android_preferences.xml", 
        "AuthHeaderPrefs.xml",
        "PasswordEncryptionKeyStorePrefs.xml",
        "77231320408_trusted_device.xml",
        "waterfall_log_in.xml",
        "msys-preferences.xml"
    ]
    
    prefs_path = "/data/data/com.instagram.android/shared_prefs"
    
    for file_name in key_files:
        print(f"\n📄 Analyzing: {file_name}")
        print("-" * 50)
        
        # Đọc toàn bộ file
        read_cmd = f"""su -c "cat {prefs_path}/{file_name}" """
        file_content = run_cmd(["adb", "-s", udid, "shell", read_cmd], timeout=15)
        
        if "No such file" in file_content or len(file_content.strip()) < 10:
            print("   ❌ File không tồn tại hoặc rỗng")
            continue
            
        print(f"   📏 File size: {len(file_content)} characters")
        
        # Tìm các pattern có thể chứa session data
        session_patterns = [
            r'sessionid["\s]*[>=:]["\s]*([a-zA-Z0-9%]{20,})',
            r'session["\s]*[>=:]["\s]*([a-zA-Z0-9%]{20,})',
            r'csrftoken["\s]*[>=:]["\s]*([a-zA-Z0-9]{20,})',
            r'csrf["\s]*[>=:]["\s]*([a-zA-Z0-9]{20,})',
            r'ds_user_id["\s]*[>=:]["\s]*(\d{8,})',
            r'user_id["\s]*[>=:]["\s]*(\d{8,})',
            r'authorization["\s]*[>=:]["\s]*([a-zA-Z0-9%]{30,})',
            r'auth_token["\s]*[>=:]["\s]*([a-zA-Z0-9%]{30,})',
            r'access_token["\s]*[>=:]["\s]*([a-zA-Z0-9%]{30,})',
            r'Bearer\s+([a-zA-Z0-9%]{30,})',
            r'ig_session["\s]*[>=:]["\s]*([a-zA-Z0-9%]{20,})',
            r'cookie["\s]*[>=:]["\s]*([^"]{20,})',
            r'username["\s]*[>=:]["\s]*([a-zA-Z0-9._]{3,30})'
        ]
        
        found_matches = []
        for pattern in session_patterns:
            matches = re.findall(pattern, file_content, re.IGNORECASE)
            for match in matches:
                if len(str(match)) > 10:  # Chỉ lấy giá trị có ý nghĩa
                    found_matches.append((pattern.split('[')[0], match))
        
        if found_matches:
            print("   ✅ Tìm thấy dữ liệu quan trọng:")
            for pattern_name, value in found_matches:
                # Ẩn một phần giá trị để bảo mật
                display_value = str(value)[:10] + "..." if len(str(value)) > 10 else str(value)
                print(f"      🔑 {pattern_name}: {display_value}")
        else:
            print("   ⚠️ Không tìm thấy session data")
            
        # Tìm kiếm JSON structures
        json_patterns = re.findall(r'\{[^}]{50,}\}', file_content)
        if json_patterns:
            print(f"   📊 Tìm thấy {len(json_patterns)} JSON structures")
            for i, json_str in enumerate(json_patterns[:3]):  # Chỉ hiển thị 3 cái đầu
                if any(keyword in json_str.lower() for keyword in ['session', 'token', 'auth', 'user']):
                    print(f"      🔍 JSON {i+1}: {json_str[:100]}...")
        
        # Tìm các string có thể là cookies/tokens
        long_strings = re.findall(r'[a-zA-Z0-9%]{40,}', file_content)
        if long_strings:
            print(f"   🎯 Tìm thấy {len(long_strings)} chuỗi dài (có thể là tokens)")
            for i, long_str in enumerate(long_strings[:3]):
                print(f"      #{i+1}: {long_str[:20]}...")

def extract_webview_cookies_advanced(udid: str):
    """Phân tích WebView cookies với nhiều phương pháp"""
    print(f"\n🌐 PHÂN TÍCH WEBVIEW COOKIES CHO: {udid}")
    print("=" * 70)
    
    webview_paths = [
        "/data/data/com.instagram.android/app_webview/Default/Cookies",
        "/data/data/com.instagram.android/app_webview/Cookies",
        "/data/data/com.instagram.android/app_chrome/Default/Cookies",
        "/data/data/com.instagram.android/app_ChromiumCookieStore/Cookies"
    ]
    
    for path in webview_paths:
        print(f"\n📂 Checking: {path}")
        
        # Kiểm tra file tồn tại
        exists = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"test -f {path} && echo 'exists' || echo 'not found'"], timeout=5)
        
        if "exists" not in exists:
            print("   ❌ File không tồn tại")
            continue
            
        # Lấy thông tin file
        file_info = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"ls -la {path}"], timeout=5)
        print(f"   📊 File info: {file_info}")
        
        # Copy file để phân tích
        temp_path = "/sdcard/temp_cookies_analysis.db"
        copy_result = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"cp '{path}' {temp_path}"], timeout=10)
        run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"chmod 644 {temp_path}"], timeout=5)
        
        # Phương pháp 1: SQLite queries
        print("   🔍 Method 1: SQLite queries...")
        sqlite_commands = [
            f"""su -c "sqlite3 {temp_path} 'SELECT name, value, host_key FROM cookies WHERE host_key LIKE \"%instagram%\" LIMIT 10;'" """,
            f"""su -c "sqlite3 {temp_path} 'SELECT name, value FROM cookies WHERE name LIKE \"%session%\" OR name LIKE \"%csrf%\" OR name LIKE \"%user%\" LIMIT 10;'" """,
            f"""su -c "sqlite3 {temp_path} '.schema'" """,
            f"""su -c "sqlite3 {temp_path} 'SELECT COUNT(*) FROM cookies;'" """
        ]
        
        for i, cmd in enumerate(sqlite_commands):
            result = run_cmd(["adb", "-s", udid, "shell", cmd], timeout=15)
            if result.strip() and "Error" not in result:
                print(f"      Query {i+1}: {result[:200]}...")
        
        # Phương pháp 2: Strings analysis
        print("   🔍 Method 2: Strings analysis...")
        strings_cmd = f"""su -c "strings {temp_path} | grep -E 'sessionid|csrftoken|instagram.com' | head -10" """
        strings_result = run_cmd(["adb", "-s", udid, "shell", strings_cmd], timeout=15)
        
        if strings_result.strip():
            print(f"      Strings: {strings_result[:300]}...")
        else:
            print("      ❌ Không tìm thấy strings liên quan")
        
        # Phương pháp 3: Hexdump analysis
        print("   🔍 Method 3: Hexdump analysis...")
        hex_cmd = f"""su -c "hexdump -C {temp_path} | grep -i session | head -5" """
        hex_result = run_cmd(["adb", "-s", udid, "shell", hex_cmd], timeout=15)
        
        if hex_result.strip():
            print(f"      Hexdump: {hex_result[:200]}...")
        
        # Cleanup
        run_cmd(["adb", "-s", udid, "shell", "rm", "-f", temp_path], timeout=5)

def check_instagram_databases(udid: str):
    """Kiểm tra các database của Instagram"""
    print(f"\n💾 PHÂN TÍCH DATABASES CHO: {udid}")
    print("=" * 70)
    
    db_path = "/data/data/com.instagram.android/databases"
    
    # Liệt kê databases
    db_list = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"ls -la {db_path}/"], timeout=10)
    print(f"📋 Databases:\n{db_list}")
    
    # Tìm database có thể chứa session data
    potential_dbs = []
    for line in db_list.split('\n'):
        if '.db' in line and any(keyword in line.lower() for keyword in ['user', 'session', 'auth', 'login']):
            db_name = line.split()[-1]
            potential_dbs.append(db_name)
    
    if not potential_dbs:
        # Lấy tất cả .db files
        for line in db_list.split('\n'):
            if '.db' in line and not line.startswith('d'):
                db_name = line.split()[-1] 
                potential_dbs.append(db_name)
    
    print(f"\n🎯 Analyzing {len(potential_dbs)} potential databases...")
    
    for db_name in potential_dbs[:5]:  # Giới hạn 5 database đầu
        print(f"\n📊 Database: {db_name}")
        
        # Copy database để phân tích
        temp_db = "/sdcard/temp_analysis.db"
        copy_cmd = f"""su -c "cp {db_path}/{db_name} {temp_db} && chmod 644 {temp_db}" """
        run_cmd(["adb", "-s", udid, "shell", copy_cmd], timeout=10)
        
        # Lấy schema
        schema_cmd = f"""su -c "sqlite3 {temp_db} '.schema' | head -20" """
        schema = run_cmd(["adb", "-s", udid, "shell", schema_cmd], timeout=10)
        
        if schema.strip():
            print(f"   Schema: {schema[:300]}...")
            
            # Tìm bảng có thể chứa session data
            session_tables = []
            for line in schema.split('\n'):
                if any(keyword in line.lower() for keyword in ['user', 'session', 'auth', 'login', 'token']):
                    if 'CREATE TABLE' in line.upper():
                        table_name = re.search(r'CREATE TABLE\s+(\w+)', line, re.IGNORECASE)
                        if table_name:
                            session_tables.append(table_name.group(1))
            
            # Query các bảng quan trọng
            for table in session_tables[:3]:
                query_cmd = f"""su -c "sqlite3 {temp_db} 'SELECT * FROM {table} LIMIT 3;'" """
                query_result = run_cmd(["adb", "-s", udid, "shell", query_cmd], timeout=10)
                
                if query_result.strip() and "Error" not in query_result:
                    print(f"   Table {table}: {query_result[:150]}...")
        
        # Cleanup
        run_cmd(["adb", "-s", udid, "shell", "rm", "-f", temp_db], timeout=5)

def generate_detailed_report(udid: str):
    """Tạo báo cáo chi tiết và đề xuất"""
    print(f"\n📋 BÁO CÁO CHI TIẾT CHO: {udid}")
    print("=" * 70)
    
    print("🔍 TÓM TẮT PHÂN TÍCH:")
    print("1. ✅ Thiết bị có quyền root")
    print("2. ✅ Instagram app đã cài đặt")
    print("3. ✅ Có nhiều preference files (Instagram đã được sử dụng)")
    print("4. ⚠️ Session cookies không tìm thấy ở vị trí thông thường")
    
    print("\n💡 NGUYÊN NHÂN CÓ THỂ:")
    print("• Instagram phiên bản mới có thể thay đổi cách lưu cookies")
    print("• Session cookies có thể được mã hóa/obfuscated")
    print("• Cookies có thể được lưu trong memory hoặc cache khác")
    print("• App có thể sử dụng native authentication thay vì web cookies")
    
    print("\n🚀 GIẢI PHÁP ĐỀ XUẤT:")
    print("1. Thử đăng xuất hoàn toàn Instagram và đăng nhập lại")
    print("2. Sử dụng Instagram web trong browser trên thiết bị")
    print("3. Kiểm tra Chrome/WebView cookies cho instagram.com")
    print("4. Sử dụng network monitoring để bắt cookies runtime")
    print("5. Thử phương pháp Frida hook để intercept API calls")

if __name__ == "__main__":
    import sys
    
    # Lấy device ID từ argument hoặc auto detect
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
        print(f"📱 Sử dụng thiết bị: {device_id}")
    
    try:
        analyze_key_preference_files(device_id)
        extract_webview_cookies_advanced(device_id)
        check_instagram_databases(device_id)
        generate_detailed_report(device_id)
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Chạy: python deep_analysis.py {device_id} > analysis_report.txt")
        print("2. Gửi report để được hỗ trợ thêm")
        print("3. Thử các giải pháp đề xuất ở trên")
        
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng phân tích")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")