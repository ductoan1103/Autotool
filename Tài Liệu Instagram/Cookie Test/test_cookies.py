#!/usr/bin/env python3
"""
Test script để kiểm tra chức năng lấy cookies Instagram từ thiết bị root
"""

import subprocess
import re

def run_cmd(cmd: list[str], timeout: float = 30.0) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return out.strip()
    except Exception as e:
        return str(e)

def test_cookie_extraction(udid: str):
    """
    Test chức năng lấy cookie từ thiết bị - Phiên bản cải thiện
    """
    print(f"🔄 Testing cookie extraction for device: {udid}")
    
    # Kiểm tra ADB connection
    devices_output = run_cmd(["adb", "devices"])
    if udid not in devices_output:
        print(f"❌ Device {udid} not found or not connected")
        return
    
    print("✅ Device connected")
    
    # Test root access
    print("🔐 Checking root access...")
    root_check = run_cmd(["adb", "-s", udid, "shell", "su", "-c", "id"], timeout=10)
    if "uid=0" in root_check:
        print("✅ Root access confirmed")
    else:
        print(f"❌ No root access: {root_check}")
        return
    
    # Check Instagram app
    print("📱 Checking Instagram app...")
    pkg_check = run_cmd(["adb", "-s", udid, "shell", "pm", "list", "packages", "com.instagram.android"])
    if "com.instagram.android" in pkg_check:
        print("✅ Instagram app found")
    else:
        print("❌ Instagram app not installed")
        return
    
    # Check if Instagram is running
    print("🔍 Checking Instagram process...")
    ps_output = run_cmd(["adb", "-s", udid, "shell", "ps | grep instagram"], timeout=10)
    if ps_output.strip():
        print(f"✅ Instagram is running: {ps_output}")
    else:
        print("⚠️ Instagram is not currently running")
    
    # Test preferences access
    print("📁 Checking preferences access...")
    prefs_path = "/data/data/com.instagram.android/shared_prefs"
    prefs_list = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"ls -la {prefs_path}"], timeout=15)
    
    if "Permission denied" not in prefs_list and "No such file" not in prefs_list:
        print("✅ Can access Instagram preferences")
        print(f"📋 Preferences files:\n{prefs_list[:300]}...")
        
        # Count XML files
        xml_count = prefs_list.count('.xml')
        print(f"📄 Found {xml_count} XML preference files")
    else:
        print(f"❌ Cannot access preferences: {prefs_list}")
        return
    
    # Test session search with multiple patterns
    print("🔍 Searching for session data...")
    search_patterns = ["sessionid", "csrftoken", "ds_user_id", "session", "auth", "login", "token"]
    
    found_any = False
    for pattern in search_patterns:
        session_cmd = f"""su -c "cd {prefs_path} && grep -ri '{pattern}' *.xml 2>/dev/null | head -2" """
        session_output = run_cmd(["adb", "-s", udid, "shell", session_cmd], timeout=20)
        
        if session_output and len(session_output.strip()) > 0:
            print(f"   ✅ Found '{pattern}': {session_output[:150]}...")
            found_any = True
        else:
            print(f"   ❌ No '{pattern}' found")
    
    if not found_any:
        print("⚠️ No session data found in preferences!")
        print("💡 Try these steps:")
        print("   1. Open Instagram app")
        print("   2. Login to your account")
        print("   3. Browse for a few minutes")
        print("   4. Run this test again")
    
    # Check WebView cookies
    print("\n🌐 Checking WebView cookies...")
    webview_paths = [
        "/data/data/com.instagram.android/app_webview/Default/Cookies",
        "/data/data/com.instagram.android/app_webview/Cookies",
        "/data/data/com.instagram.android/app_chrome/Default/Cookies"
    ]
    
    webview_found = False
    for path in webview_paths:
        exists = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"test -f {path} && echo 'exists' || echo 'not found'"], timeout=5)
        
        if "exists" in exists:
            print(f"   ✅ WebView cookies found: {path}")
            file_size = run_cmd(["adb", "-s", udid, "shell", "su", "-c", f"ls -la {path}"], timeout=5)
            print(f"      {file_size}")
            webview_found = True
        else:
            print(f"   ❌ Not found: {path}")
    
    if webview_found:
        print("   💡 WebView cookies available - may contain session data")
    
    # Summary
    print("\n📋 SUMMARY:")
    if found_any or webview_found:
        print("   ✅ Device looks good for cookie extraction!")
        print("   🚀 You can try running the main cookie extractor now")
    else:
        print("   ⚠️ No session data found")
        print("   📝 Recommendations:")
        print("      1. Make sure you're logged into Instagram")
        print("      2. Use Instagram app for a few minutes")
        print("      3. Try logging out and back in")
        print("      4. Restart the device")
    
    print("🏁 Test completed!")
    
    return found_any or webview_found

if __name__ == "__main__":
    # Lấy danh sách devices
    devices_output = run_cmd(["adb", "devices"])
    lines = [l for l in devices_output.splitlines() if l.strip()]
    devices = [ln.split("\t")[0] for ln in lines[1:] if "\tdevice" in ln]
    
    if not devices:
        print("❌ No devices found. Please connect your device and enable USB debugging.")
    else:
        print(f"📱 Found devices: {devices}")
        for device in devices:
            test_cookie_extraction(device)
            print("\n" + "="*50 + "\n")