#!/usr/bin/env python3
"""
Test Instagram Cookies API
Kiểm tra cookies có hoạt động với Instagram API không
"""

import requests
import json
import sys

def test_instagram_cookies(cookie_string, username="hoang68358"):
    """
    Test Instagram cookies với các API endpoint
    """
    print(f"🧪 TESTING INSTAGRAM COOKIES")
    print("=" * 50)
    print(f"👤 Username: {username}")
    print(f"🍪 Cookie: {cookie_string[:50]}...")
    
    # Headers chuẩn Instagram
    headers = {
        "Cookie": cookie_string,
        "User-Agent": "Instagram 123.0.0.21.114 Android (23/6.0.1; 640dpi; 1440x2560; samsung; SM-G935F; herolte; samsungexynos8890; en_US)",
        "Accept": "*/*",
        "Accept-Language": "en-US",
        "Accept-Encoding": "gzip, deflate",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "close"
    }
    
    # Parse CSRF token từ cookies
    csrf_token = ""
    for part in cookie_string.split("; "):
        if part.startswith("csrftoken="):
            csrf_token = part.split("=", 1)[1]
            break
    
    if csrf_token:
        headers["X-CSRFToken"] = csrf_token
        headers["X-Instagram-AJAX"] = csrf_token
    
    test_results = []
    
    # TEST 1: Profile page
    print(f"\n1️⃣ Testing profile page...")
    try:
        response = requests.get(f"https://www.instagram.com/{username}/", headers=headers, timeout=10)
        
        success = response.status_code == 200
        has_user_data = '"username"' in response.text and username in response.text
        is_logged_in = '"is_logged_in":true' in response.text or 'sessionid' in response.cookies
        
        print(f"   Status: {response.status_code}")
        print(f"   ✅ Profile loaded: {success}")
        print(f"   ✅ User data found: {has_user_data}")
        print(f"   ✅ Logged in: {is_logged_in}")
        
        test_results.append({
            "test": "Profile Page",
            "success": success and has_user_data,
            "status_code": response.status_code,
            "logged_in": is_logged_in
        })
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append({
            "test": "Profile Page", 
            "success": False,
            "error": str(e)
        })
    
    # TEST 2: Instagram Web API
    print(f"\n2️⃣ Testing Instagram Web API...")
    try:
        api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        response = requests.get(api_url, headers=headers, timeout=10)
        
        success = response.status_code == 200
        has_json = False
        user_id = None
        
        if success:
            try:
                data = response.json()
                has_json = True
                user_data = data.get("data", {}).get("user", {})
                user_id = user_data.get("id")
                print(f"   ✅ API response: Valid JSON")
                print(f"   ✅ User ID: {user_id}")
            except:
                print(f"   ❌ Invalid JSON response")
        
        print(f"   Status: {response.status_code}")
        
        test_results.append({
            "test": "Web API",
            "success": success and has_json,
            "status_code": response.status_code,
            "user_id": user_id
        })
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append({
            "test": "Web API",
            "success": False, 
            "error": str(e)
        })
    
    # Tổng kết
    print(f"\n📊 SUMMARY:")
    print("-" * 30)
    
    total_tests = len(test_results)
    successful_tests = sum(1 for t in test_results if t["success"])
    
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests > 0:
        print(f"\n✅ COOKIES WORKING!")
        print(f"🎯 Recommended use cases:")
        print(f"   • Web scraping Instagram profiles")
        print(f"   • Automation scripts")  
        print(f"   • API requests with authentication")
    else:
        print(f"\n❌ COOKIES NOT WORKING")
        print(f"💡 Possible solutions:")
        print(f"   • Get fresh cookies from logged-in device")
        print(f"   • Check if account is banned/restricted")
        print(f"   • Try different User-Agent string")
        print(f"   • Use cookies immediately after generation")
    
    return test_results

if __name__ == "__main__":
    # Đọc cookie từ file session
    session_files = [
        "instagram_session_hoang68358_33008a43.json",
        "instagram_session_hoang68358.json"
    ]
    
    cookie_string = None
    username = "hoang68358"
    
    # Thử đọc từ file
    for file_path in session_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cookie_string = data.get("cookie_string")
                username = data.get("username", username)
                print(f"📁 Loaded session from: {file_path}")
                break
        except:
            continue
    
    # Hoặc sử dụng từ command line
    if len(sys.argv) > 1:
        cookie_string = sys.argv[1]
    
    # Hoặc cookie mặc định từ generate trước đó
    if not cookie_string:
        cookie_string = "sessionid=77231320408%3A66627f3bce177656a2bea624609; ds_user_id=77231320408; csrftoken=b58fe6af5b293a460f8baf5ac42d5a84; mid=kPuMF_5KaBIr; ig_did=ANDROIDD4E884E3971F0DC4; rur=VLL; ig_nrcb=1"
    
    if cookie_string:
        test_results = test_instagram_cookies(cookie_string, username)
        
        # Lưu kết quả test
        with open(f"test_results_{username}.json", 'w') as f:
            json.dump(test_results, f, indent=2)
        print(f"\n💾 Test results saved to: test_results_{username}.json")
    else:
        print("❌ No cookie string provided")
        print("Usage: python test_instagram_api.py '<cookie_string>'")
        print("Or place session JSON file in same directory")