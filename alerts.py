import httpx
from app.settings import settings

async def maybe_alert(result):
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return
    if result["risk_score"] < settings.alert_threshold:
        return
    text = (
        f"🚨 Solana Risk Alert\n"
        f"Token: {result['mint']}\n"
        f"Risk: {result['risk_score']}/100 ({result['risk_level']})\n"
        f"Mint authority: {'ACTIVE' if result['authority']['mint_active'] else 'OFF'}\n"
        f"Freeze authority: {'ACTIVE' if result['authority']['freeze_active'] else 'OFF'}\n"
        f"Top 10: {result['holders']['top10_pct']}%"
    )
    url=f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json={"chat_id":settings.telegram_chat_id,"text":text})
