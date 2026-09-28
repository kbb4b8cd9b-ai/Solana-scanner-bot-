from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.scanner import scan_token
from app.db import init_db, save_scan, list_scans
from app.alerts import maybe_alert
from app.settings import settings

app = FastAPI(title="Solana Risk Scanner", version="1.0.0")

@app.on_event("startup")
def startup():
    init_db()

class ScanRequest(BaseModel):
    mint: str

@app.get("/", response_class=HTMLResponse)
def home():
    with open("app/static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/health")
def health():
    return {"ok": True, "service": "solana-risk-scanner"}

@app.post("/api/scan")
async def scan(req: ScanRequest):
    try:
        result = await scan_token(req.mint)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"RPC/analysis error: {e}")
    save_scan(result)
    await maybe_alert(result)
    return result

@app.get("/api/scan/{mint}")
def latest_scan(mint: str):
    rows = list_scans(mint=mint, limit=1)
    if not rows:
        raise HTTPException(status_code=404, detail="No scan found")
    return rows[0]

@app.get("/api/scans")
def scans():
    return list_scans(limit=50)
