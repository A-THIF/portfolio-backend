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
    
    # 💡 Pro Tip: Using Markdown [Text](Link) makes the link clickable
    # If no link provided, we just show "None"
    formatted_link = f"[{profile_link}]({profile_link})" if profile_link and "http" in profile_link else "None"

    body = (
        "🕹️ *New Lockscreen Entry*\n"
        "--------------------------\n"
        f"👤 *Name:* {name}\n"
        f"📧 *Email:* {email if email else 'Not provided'}\n"
        f"🔗 *Profile:* {formatted_link}\n"
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
                "parse_mode": "Markdown",
                "disable_web_page_preview": False # Shows a preview of their profile link
            })
        except Exception as e:
            print(f"Telegram Notification Failed: {e}")