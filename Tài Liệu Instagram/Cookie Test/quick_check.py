#!/usr/bin/env python3
"""
Quick test script cho Instagram Cookie Extractor
Kiểm tra nhanh thiết bị và khả năng lấy cookies
"""

import subprocess
import sys

def run_cmd(cmd: list[str]) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=10)
        return out.strip()
    except Exception as e:
        return str(e)

def quick_check():
    print("🔍 KIỂM TRA NHANH COOKIE EXTRACTOR")
    print("=" * 50)
    
    # 1. Kiểm tra ADB
    print("1️⃣ Kiểm tra ADB...")
    try:
        adb_version = run_cmd(["adb", "version"])
        if "Android Debug Bridge" in adb_version:
            print("✅ ADB có sẵn")
        else:
            print("❌ ADB không hoạt động")
            return
    except:
        print("❌ ADB không được cài đặt")
        print("   Cài đặt Android SDK Platform Tools")
        return
    
    # 2. Kiểm tra thiết bị
    print("2️⃣ Tìm thiết bị...")
    devices_output = run_cmd(["adb", "devices"])
    lines = [l for l in devices_output.splitlines() if l.strip()]
    devices = [ln.split("\t")[0] for ln in lines[1:] if "\tdevice" in ln]
    
    if not devices:
        print("❌ Không tìm thấy thiết bị")
        print("   - Kết nối USB và bật USB Debugging")
        print("   - Chấp nhận USB Debugging trên thiết bị")
        return
    
    print(f"✅ Tìm thấy {len(devices)} thiết bị: {devices}")
    
    # 3. Kiểm tra từng thiết bị
    for device in devices:
        print(f"\n3️⃣ Kiểm tra thiết bị: {device}")
        
        # Root check
        root_check = run_cmd(["adb", "-s", device, "shell", "su", "-c", "id"])
        if "uid=0" in root_check:
            print("   ✅ Có quyền root")
        else:
            print("   ❌ Không có quyền root")
            print("   ⚠️ Cần root để lấy cookies")
            continue
        
        # Instagram check
        pkg_check = run_cmd(["adb", "-s", device, "shell", "pm", "list", "packages", "com.instagram.android"])
        if "com.instagram.android" in pkg_check:
            print("   ✅ Instagram đã cài đặt")
        else:
            print("   ❌ Instagram chưa cài đặt")
            continue
        
        # Data access check
        data_check = run_cmd(["adb", "-s", device, "shell", "su", "-c", "ls /data/data/com.instagram.android"])
        if "Permission denied" not in data_check and "No such file" not in data_check:
            print("   ✅ Có thể truy cập dữ liệu Instagram")
            print(f"   📁 Device {device} SẴN SÀNG lấy cookies!")
        else:
            print("   ❌ Không thể truy cập dữ liệu Instagram")
    
    print("\n" + "=" * 50)
    print("🎯 Kết luận:")
    print("- Nếu thấy 'SẴN SÀNG', bạn có thể lấy cookies")
    print("- Chạy AutoNuoiAccIns.py và bấm '🍪 Get Cookies (ROOT)'")
    print("- Đảm bảo đã đăng nhập Instagram trước")

if __name__ == "__main__":
    quick_check()