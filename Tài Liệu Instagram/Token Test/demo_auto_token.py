#!/usr/bin/env python3
"""
Demo test Instagram Token trong Auto.py với thiết bị thực
"""

from Auto import AndroidWorker

def test_auto_token_with_device():
    """Test token function trong Auto.py với thiết bị thực"""
    # Sử dụng device đã biết
    test_udid = "33008a430e2ca375"
    
    print(f"🔍 Testing Auto.py Instagram token với device: {test_udid}")
    print("="*60)
    
    # Tạo AndroidWorker instance
    try:
        worker = AndroidWorker(test_udid)
        print(f"✅ Khởi tạo AndroidWorker: {test_udid}")
        
        # Test get token
        print(f"\n🔑 Testing get_instagram_token()...")
        token_info = worker.get_instagram_token()
        
        print(f"\n📊 KẾT QUẢ TOKEN:")
        print(f"✅ Success: {token_info.get('success', False)}")
        
        if token_info.get('success'):
            print(f"👤 Username: {token_info.get('username', 'N/A')}")
            print(f"🆔 User ID: {token_info.get('user_id', 'N/A')}")
            print(f"📱 App ID: {token_info.get('app_id', 'N/A')}")
            print(f"🔧 Method: {token_info.get('method', 'N/A')}")
            print(f"⏰ Expires: {token_info.get('expires_at', 'N/A')}")
            print(f"🔑 Access Token: {token_info.get('access_token', '')[:50]}...")
            
            # Test format function
            bearer_token = worker.format_token_for_api(token_info)
            print(f"🔐 Bearer Format: {bearer_token[:70]}...")
            
            # Demo định dạng Live.txt và Die.txt
            print(f"\n💾 ĐỊNH DẠNG FILE:")
            demo_username = token_info.get('username', 'demo_user')
            demo_password = "demo_pass123"
            demo_email = "demo@temp.com"
            demo_cookie = "sessionid=demo123..."
            demo_token = token_info.get('access_token', '')
            
            live_format = f"{demo_username}|{demo_password}|{demo_email}|{demo_cookie}|{demo_token}|"
            die_format = f"{demo_username}|{demo_password}|{demo_email}|{demo_cookie}|{demo_token}|"
            
            print(f"📄 Live.txt format:")
            print(f"   {live_format[:100]}...")
            print(f"📄 Die.txt format:")
            print(f"   {die_format[:100]}...")
            
            # API examples
            print(f"\n🌐 API USAGE EXAMPLES:")
            print(f"curl -H \"Authorization: {bearer_token}\" \\")
            print(f"     \"https://graph.instagram.com/me?fields=id,username\"")
            print(f"")
            print(f"# Python requests")
            print(f"headers = {{'Authorization': '{bearer_token[:50]}...'}}")
            print(f"response = requests.get('https://graph.instagram.com/me', headers=headers)")
            
        else:
            print(f"❌ Error: {token_info.get('error', 'Unknown error')}")
            print(f"\n💡 Gợi ý:")
            print(f"- Đảm bảo thiết bị đã đăng nhập Instagram")
            print(f"- Kiểm tra quyền root")
            print(f"- Thử mở Instagram app trước")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_auto_token_with_device()