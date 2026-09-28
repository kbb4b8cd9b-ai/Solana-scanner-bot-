import httpx
from base58 import b58decode
from app.settings import settings

TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

async def rpc(method, params):
    payload = {"jsonrpc":"2.0","id":1,"method":method,"params":params}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(settings.rpc_url, json=payload)
        r.raise_for_status()
        data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data["result"]

async def get_account(address):
    return await rpc("getAccountInfo", [address, {"encoding":"base64"}])

async def get_token_accounts_by_mint(mint):
    return await rpc("getTokenAccountsByOwner", [mint, {"programId": TOKEN_PROGRAM}])

async def get_token_supply(mint):
    return await rpc("getTokenSupply", [mint])

async def get_token_accounts(mint):
    return await rpc("getProgramAccounts", [
        TOKEN_PROGRAM,
        {"encoding":"jsonParsed",
         "filters":[{"dataSize":165},{"memcmp":{"offset":0,"bytes":mint}}]}
    ])
