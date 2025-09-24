#!/usr/bin/env python3
"""
Instagram Cookie Troubleshooting Tool
Giúp debug vấn đề lấy cookies từ thiết bị root
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

def detailed_instagram_analysis(udid: str):
    """Phân tích chi tiết Instagram trên thiết bị"""
    print(f"🔍 PHÂN TÍCH CHI TIẾT CHO THIẾT BỊ: {udid}")
    print("=" * 60)
    
    # 1. Kiểm tra Instagram process
    print("1️⃣ Kiểm tra Instagram process...")
    ps_cmd = """su -c "ps | grep instagram" """
    ps_output = run_cmd(["adb", "-s", udid, "shell", ps_cmd], timeout=10)
    print(f"   Process: {ps_output if ps_output else 'Không có process nào'}")
    
    # 2. Kiểm tra thời gian truy cập cuối của files
    print("\n2️⃣ Kiểm tra thời gian truy cập files...")
    app_path = "/data/data/com.instagram.android"
    access_times = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"stat {app_path}/shared_prefs/*.xml | grep Modify"], timeout=15)
    print(f"   Thời gian modify files:\n{access_times[:300]}...")
    
    # 3. Liệt kê tất cả files preferences
    print("\n3️⃣ Tất cả files preferences...")
    prefs_list = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"ls -la {app_path}/shared_prefs/"], timeout=10)
    print(f"   Files:\n{prefs_list}")
    
    # 4. Tìm kiếm bất kỳ dấu vết session nào
    print("\n4️⃣ Tìm kiếm dấu vết session...")
    search_terms = ["session", "auth", "login", "token", "cookie", "user"]
    
    for term in search_terms:
        print(f"\n   🔍 Tìm '{term}'...")
        search_cmd = f"""su -c "cd {app_path}/shared_prefs && grep -ri '{term}' *.xml 2>/dev/null | head -3" """
        search_result = run_cmd(["adb", "-s", udid, "shell", search_cmd], timeout=15)
        
        if search_result.strip():
            print(f"      ✅ Tìm thấy: {search_result[:200]}...")
        else:
            print(f"      ❌ Không tìm thấy")
    
    # 5. Kiểm tra databases
    print("\n5️⃣ Kiểm tra databases...")
    db_path = f"{app_path}/databases"
    db_list = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"ls -la {db_path}/"], timeout=10)
    print(f"   Databases:\n{db_list}")
    
    # 6. Kiểm tra cache và files
    print("\n6️⃣ Kiểm tra cache và files...")
    cache_files = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"find {app_path}/cache -name '*session*' -o -name '*auth*' -o -name '*cookie*' 2>/dev/null"], timeout=15)
    files_files = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"find {app_path}/files -name '*session*' -o -name '*auth*' -o -name '*cookie*' 2>/dev/null"], timeout=15)
    
    print(f"   Cache files: {cache_files if cache_files else 'Không có'}")
    print(f"   App files: {files_files if files_files else 'Không có'}")
    
    # 7. Kiểm tra WebView
    print("\n7️⃣ Kiểm tra WebView cookies...")
    webview_paths = [
        f"{app_path}/app_webview/Default/Cookies",
        f"{app_path}/app_webview/Cookies",
        f"{app_path}/app_chrome/Default/Cookies"
    ]
    
    for path in webview_paths:
        exists = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"test -f {path} && echo 'exists' || echo 'not found'"], timeout=5)
        print(f"   {path}: {exists}")
        
        if "exists" in exists:
            # Kiểm tra size và thời gian
            file_info = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"ls -la {path}"], timeout=5)
            print(f"      Info: {file_info}")
    
    # 8. Dump một file preferences để xem cấu trúc
    print("\n8️⃣ Dump sample preference file...")
    sample_file = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"ls {app_path}/shared_prefs/*.xml | head -1"], timeout=5)
    
    if sample_file.strip():
        print(f"   Sample file: {sample_file}")
        file_content = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"cat '{sample_file.strip()}' | head -20"], timeout=10)
        print(f"   Content:\n{file_content}")
    
    # 9. Kiểm tra Instagram version
    print("\n9️⃣ Instagram version...")
    version_info = run_cmd(["adb", "-s", udid, "shell", "dumpsys", "package", "com.instagram.android", "|", "grep", "versionName"], timeout=10)
    print(f"   Version: {version_info if version_info else 'Không xác định'}")
    
    print("\n" + "=" * 60)
    print("🎯 KHUYẾN NGHỊ:")
    print("1. Nếu không thấy file preferences nào → Instagram chưa được setup")
    print("2. Nếu thấy files nhưng không có session data → Chưa đăng nhập hoặc session expired")
    print("3. Nếu thấy WebView cookies → Có thể cần đọc từ SQLite")
    print("4. Thử mở Instagram app, navigate một chút, rồi chạy lại")

def force_generate_session(udid: str):
    """Cố gắng trigger tạo session mới"""
    print(f"\n🔄 FORCE GENERATE SESSION CHO: {udid}")
    print("=" * 50)
    
    # 1. Kill Instagram process
    print("1️⃣ Killing Instagram process...")
    kill_cmd = """su -c "am force-stop com.instagram.android" """
    run_cmd(["adb", "-s", udid, "shell", kill_cmd], timeout=10)
    
    # 2. Clear cache (optional)
    print("2️⃣ Clearing app cache...")
    cache_cmd = """su -c "rm -rf /data/data/com.instagram.android/cache/*" """
    run_cmd(["adb", "-s", udid, "shell", cache_cmd], timeout=10)
    
    # 3. Start Instagram
    print("3️⃣ Starting Instagram...")
    start_cmd = """am start -n com.instagram.android/com.instagram.mainactivity.MainActivity"""
    run_cmd(["adb", "-s", udid, "shell", start_cmd], timeout=10)
    
    print("✅ Đã khởi động lại Instagram")
    print("⏰ Hãy đợi 30 giây, mở Instagram, đăng nhập và browse một chút")
    print("🔄 Sau đó chạy lại cookie extractor")

if __name__ == "__main__":
    # Lấy devices
    devices_output = run_cmd(["adb", "devices"])
    lines = [l for l in devices_output.splitlines() if l.strip()]
    devices = [ln.split("\t")[0] for ln in lines[1:] if "\tdevice" in ln]
    
    if not devices:
        print("❌ Không tìm thấy thiết bị")
        exit(1)
    
    print(f"📱 Tìm thấy thiết bị: {devices}")
    
    for device in devices:
        detailed_instagram_analysis(device)
        
        print(f"\n❓ Bạn có muốn force restart Instagram trên {device}? (y/n): ", end="")
        try:
            choice = input().lower()
            if choice == 'y':
                force_generate_session(device)
        except:
            pass
        
        print("\n" + "="*80 + "\n")