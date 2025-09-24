#!/usr/bin/env python3
"""
Demo test Instagram Token với thiết bị thực
"""

from AutoNuoiAccIns import get_instagram_token, format_token_for_api
import json

def test_token_with_device():
    """Test token function với thiết bị thực"""
    # Sử dụng device từ conversation trước
    test_udid = "33008a430e2ca375"
    
    print(f"🔍 Testing Instagram token với device: {test_udid}")
    print("="*60)
    
    # Test get token
    try:
        token_info = get_instagram_token(test_udid, debug_mode=True)
        
        print(f"\n📊 KẾT QUẢ TOKEN:")
        print(f"✅ Success: {token_info['success']}")
        
        if token_info['success']:
            print(f"👤 Username: {token_info['username']}")
            print(f"🆔 User ID: {token_info['user_id']}")
            print(f"📱 App ID: {token_info['app_id']}")
            print(f"🔧 Method: {token_info['method']}")
            print(f"⏰ Expires: {token_info.get('expires_at', 'N/A')}")
            print(f"🔑 Access Token: {token_info['access_token'][:50]}...")
            
            # Test format function
            bearer_token = format_token_for_api(token_info)
            print(f"🔐 Bearer Format: {bearer_token[:70]}...")
            
            # Demo API usage
            print(f"\n💡 API USAGE EXAMPLES:")
            print(f"curl -H \"Authorization: {bearer_token}\" \\")
            print(f"     \"https://graph.instagram.com/me?fields=id,username\"")
            print(f"")
            print(f"# Python requests")
            print(f"headers = {{'Authorization': '{bearer_token}'}}")
            print(f"response = requests.get('https://graph.instagram.com/me', headers=headers)")
            
            # Lưu demo file
            demo_data = {
                "device_id": test_udid,
                "token_info": token_info,
                "bearer_format": bearer_token,
                "api_examples": {
                    "profile": "https://graph.instagram.com/me?fields=id,username",
                    "media": "https://graph.instagram.com/me/media",
                    "posts": "https://graph.instagram.com/{media-id}"
                }
            }
            
            with open("demo_instagram_token.json", 'w', encoding='utf-8') as f:
                json.dump(demo_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Đã lưu demo data: demo_instagram_token.json")
            
        else:
            print(f"❌ Error: {token_info['error']}")
            print(f"\n💡 Gợi ý:")
            print(f"- Đảm bảo thiết bị đã đăng nhập Instagram")
            print(f"- Kiểm tra quyền root")
            print(f"- Thử mở Instagram app trước")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_token_with_device()