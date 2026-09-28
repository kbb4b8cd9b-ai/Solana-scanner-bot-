# Solana Risk Scanner — MVP V1

Mobile-friendly Solana token risk scanner.

## What it does
- Reads a Solana mint account from an RPC endpoint.
- Checks mint authority and freeze authority.
- Reads token supply.
- Collects token-account balances to estimate holder concentration.
- Produces an explainable 0–100 risk score.
- Stores scans in SQLite by default.
- Optional Telegram alerts.
- Optional PostgreSQL via DATABASE_URL.

## Important
This is a defensive analytics tool. A high score is a risk indicator, not proof of fraud.
The MVP deliberately does not place trades or send transactions.

## Run in Codespaces
1. Copy `.env.example` to `.env`.
2. Set `SOLANA_RPC_URL` (a public RPC can be used for testing).
3. Install dependencies:
   `pip install -r requirements.txt`
4. Start:
   `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Open port 8000 in the browser.

API:
- `GET /api/health`
- `POST /api/scan` with `{"mint":"TOKEN_MINT_ADDRESS"}`
- `GET /api/scan/{mint}`
- `GET /api/scans`

Dashboard:
- `GET /`
