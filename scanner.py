import base64, struct
from datetime import datetime, timezone
from app.solana import rpc
from app.settings import settings

TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

def parse_mint_account(value):
    if not value:
        raise ValueError("Mint account not found")
    data = value["data"]
    raw = base64.b64decode(data[0])
    # SPL Mint layout: mintAuthorityOption u32, mintAuthority pubkey,
    # supply u64, decimals u8, initialized u8, freezeAuthorityOption u32,
    # freezeAuthority pubkey.
    if len(raw) < 82:
        raise ValueError("Invalid SPL mint account")
    mint_opt = struct.unpack_from("<I", raw, 0)[0]
    mint_auth = raw[4:36].hex() if mint_opt else None
    supply = struct.unpack_from("<Q", raw, 36)[0]
    decimals = raw[44]
    freeze_opt = struct.unpack_from("<I", raw, 46)[0]
    freeze_auth = raw[50:82].hex() if freeze_opt else None
    return {
        "mint_authority_active": bool(mint_opt),
        "mint_authority_raw": mint_auth,
        "freeze_authority_active": bool(freeze_opt),
        "freeze_authority_raw": freeze_auth,
        "raw_supply": supply,
        "decimals": decimals,
        "supply": supply / (10 ** decimals)
    }

def holder_metrics(accounts, supply):
    holders = []
    for item in accounts:
        try:
            info = item["account"]["data"]["parsed"]["info"]
            amount = int(info["tokenAmount"]["amount"])
            owner = info.get("owner", "unknown")
            if amount > 0:
                holders.append((owner, amount))
        except Exception:
            continue
    holders.sort(key=lambda x:x[1], reverse=True)
    total = sum(x[1] for x in holders) or 1
    def pct(n):
        return round(sum(x[1] for x in holders[:n]) / total * 100, 2)
    return {
        "holder_count": len(holders),
        "top1_pct": pct(1),
        "top5_pct": pct(5),
        "top10_pct": pct(10),
        "top20_pct": pct(20),
        "top50_pct": pct(50),
        "top_holders": [{"owner":o, "raw_amount":a, "pct":round(a/total*100,2)} for o,a in holders[:10]]
    }

def score_authority(m):
    score = 0
    reasons = []
    if m["mint_authority_active"]:
        score += 15; reasons.append("Mint authority is active")
    if m["freeze_authority_active"]:
        score += 15; reasons.append("Freeze authority is active")
    return min(score, 30), reasons

def score_holders(h):
    score = 0; reasons=[]
    if h["top10_pct"] >= 80: score += 25; reasons.append("Top 10 holders control >=80%")
    elif h["top10_pct"] >= 60: score += 18; reasons.append("Top 10 holders control >=60%")
    elif h["top10_pct"] >= 40: score += 10; reasons.append("Top 10 holders control >=40%")
    if h["top1_pct"] >= 30: score += 10; reasons.append("Largest holder controls >=30%")
    elif h["top1_pct"] >= 15: score += 5; reasons.append("Largest holder controls >=15%")
    return min(score, 35), reasons

def score_trading_placeholder():
    # V1 has no historical trade indexer yet.
    return 0, ["Wash-trading analysis requires transaction history/indexer; not scored in V1"]

async def scan_token(mint):
    if len(mint) < 32 or len(mint) > 44:
        raise ValueError("Invalid Solana mint address length")
    acc = await rpc("getAccountInfo", [mint, {"encoding":"base64"}])
    m = parse_mint_account(acc["value"])
    accounts = await rpc("getProgramAccounts", [
        TOKEN_PROGRAM,
        {"encoding":"jsonParsed",
         "filters":[{"dataSize":165},{"memcmp":{"offset":0,"bytes":mint}}]}
    ])
    h = holder_metrics(accounts, m["supply"])
    a_score, a_reasons = score_authority(m)
    h_score, h_reasons = score_holders(h)
    t_score, t_reasons = score_trading_placeholder()
    total = min(100, a_score + h_score + t_score)
    if total >= 75: level="HIGH"
    elif total >= 45: level="MEDIUM"
    else: level="LOW"
    return {
        "mint": mint,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "risk_score": total,
        "risk_level": level,
        "authority": {
            "mint_active": m["mint_authority_active"],
            "freeze_active": m["freeze_authority_active"]
        },
        "supply": m["supply"],
        "decimals": m["decimals"],
        "holders": h,
        "liquidity": {
            "status": "NOT_INDEXED_V1",
            "note": "DEX liquidity integration is the next module"
        },
        "wash_trading": {
            "score": t_score,
            "status": "NOT_INDEXED_V1"
        },
        "score_breakdown": {
            "authority": a_score,
            "holders": h_score,
            "trading": t_score
        },
        "reasons": a_reasons + h_reasons + t_reasons
    }
