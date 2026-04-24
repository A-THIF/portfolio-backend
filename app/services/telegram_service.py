from datetime import datetime

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
    
    formatted_link = f"[{profile_link}]({profile_link})" if profile_link and "http" in profile_link else "None"

    body = (
        "🕹️ *New Lockscreen Entry*\n"
        "--------------------------\n"
        f"👤 *Name:* {name}\n"
        f"📧 *Email:* {email if email else 'None'}\n"
        f"🔗 *Profile:* {formatted_link}\n"
        "--------------------------\n"
        f"🌐 *IP:* `{ip}`\n"
        f"🔢 *Total Visits:* {visit_count}\n"
        f"🖥️ *User-Agent:* `{user_agent}`\n"
        f"⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": body,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False # Shows a preview of their profile link
            })
        except Exception as e:
            print(f"Telegram Notification Failed: {e}")