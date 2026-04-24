# test_tele.py
import asyncio
import os
from dotenv import load_dotenv
from app.services.telegram_service import send_visitor_notification
from app.config import settings

# Load the .env file to make sure it reads your latest credentials
load_dotenv()

async def run_test():
    print("--- 🚀 Telegram Notification Test ---")
    print(f"Target Token: {settings.TELEGRAM_TOKEN[:10]}...")
    print(f"Target Chat ID: {settings.TELEGRAM_CHAT_ID}")
    
    # Mock data based on your DB columns
    test_data = {
        "name": "Athif (Test)",
        "email": "athif@example.com",
        "profile_link": "https://github.com/athif",
        "visit_count": 5, # Testing 'Returning User' logic
        "ip": "122.174.x.x" # Mock Chennai IP
    }

    try:
        await send_visitor_notification(
            name=test_data["name"],
            email=test_data["email"],
            profile_link=test_data["profile_link"],
            visit_count=test_data["visit_count"],
            ip=test_data["ip"]
        )
        print("\n✅ Success! Check your Telegram app.")
    except Exception as e:
        print(f"\n❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())