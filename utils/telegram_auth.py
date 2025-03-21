import hmac
import hashlib
import json
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def verify_telegram_init_data(init_data: str) -> dict:
    """Xác minh và trích xuất dữ liệu từ initData của Telegram"""
    try:
        # Tạo secret key từ bot token
        secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
        # Xác minh hash
        data = {k: v for k, v in (item.split("=") for item in init_data.split("&"))}
        check_hash = data.pop("hash")
        data_str = "&".join(f"{k}={v}" for k, v in sorted(data.items()))
        computed_hash = hmac.new(secret_key, data_str.encode(), hashlib.sha256).hexdigest()
        
        if computed_hash != check_hash:
            raise ValueError("Invalid Telegram initData hash")
        
        user_data = json.loads(data["user"])
        return user_data  # Chứa id, username, v.v.
    except Exception as e:
        raise ValueError(f"Failed to verify initData: {str(e)}")