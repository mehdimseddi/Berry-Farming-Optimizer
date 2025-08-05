# backend/supabase_client.py
import os
import httpx
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()  # loads from .env in the current working directory (your project root)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

client = httpx.AsyncClient(base_url=SUPABASE_URL, headers=HEADERS)

async def save_account(account_data: Dict[str, Any]) -> Dict:
    """Save a single account to Supabase"""
    response = await client.post(
        "/rest/v1/accounts",
        json=account_data,
        params={"select": "id"}
    )
    response.raise_for_status()
    return response.json()[0]

async def get_accounts() -> List[Dict]:
    """Load all accounts from Supabase"""
    response = await client.get(
        "/rest/v1/accounts",
        params={"order": "created_at"}
    )
    response.raise_for_status()
    return response.json()

async def save_optimization_result(request: dict, response: dict, account_ids: List[str]):
    """Save full optimization result"""
    data = {
        "request": request,
        "response": response,
        "account_ids": account_ids
    }
    resp = await client.post("/rest/v1/optimization_results", json=data)
    resp.raise_for_status()
    return resp.json()