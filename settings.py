import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    database_url = os.getenv("DATABASE_URL", "sqlite:///./risk_scanner.db")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    alert_threshold = int(os.getenv("ALERT_THRESHOLD", "75"))

settings = Settings()
