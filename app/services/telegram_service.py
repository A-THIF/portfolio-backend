import httpx
from app.config import settings

async def send_visitor_notification(
    name: str, 
    email: str, 
    profile_link: str, 
    visit_count: int, 
    ip: str
):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    
    # Building a clean, readable alert for your phone
    body = (
        "🕹️ *New Lockscreen Entry*\n"
        "--------------------------\n"
        f"👤 *Name:* {name}\n"
        f"📧 *Email:* {email if email else 'Not provided'}\n"
        f"🔗 *Profile:* {profile_link if profile_link else 'None'}\n"
        "--------------------------\n"
        f"🌐 *IP:* `{ip}`\n"
        f"🔢 *Total Visits:* {visit_count}\n"
        f"✨ *Type:* {'Returning User' if visit_count > 1 else 'New User'}"
    )

    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": body,
                "parse_mode": "Markdown"
            })
        except Exception as e:
            print(f"Telegram Notification Failed: {e}") 