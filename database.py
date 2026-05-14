import httpx
from config import SUPABASE_URL, SUPABASE_KEY

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

BASE = f"{SUPABASE_URL}/rest/v1"


async def check_scam_by_id(telegram_id: int):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE}/scam_base", headers=HEADERS, params={"telegram_id": f"eq.{telegram_id}"})
        return r.json() if r.json() else None


async def check_scam_by_username(username: str):
    username = username.lower().lstrip("@")
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE}/scam_base", headers=HEADERS, params={"username": f"ilike.{username}"})
        return r.json() if r.json() else None


async def check_scam_by_phone(phone: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE}/scam_base", headers=HEADERS, params={"phone": f"eq.{phone}"})
        return r.json() if r.json() else None


async def add_to_scam_base(data: dict):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE}/scam_base", headers=HEADERS, json=data)
        return r.json()


async def create_pending_report(data: dict):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE}/pending_reports", headers=HEADERS, json=data)
        result = r.json()
        return result[0] if result else None


async def get_pending_report(report_id: int):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE}/pending_reports", headers=HEADERS, params={"id": f"eq.{report_id}"})
        result = r.json()
        return result[0] if result else None


async def update_report_status(report_id: int, status: str):
    async with httpx.AsyncClient() as client:
        await client.patch(f"{BASE}/pending_reports", headers=HEADERS, params={"id": f"eq.{report_id}"}, json={"status": status})


async def update_report_moderation_msg(report_id: int, msg_id: int):
    async with httpx.AsyncClient() as client:
        await client.patch(f"{BASE}/pending_reports", headers=HEADERS, params={"id": f"eq.{report_id}"}, json={"moderation_message_id": msg_id})


async def get_all_scammers(limit=50):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE}/scam_base", headers=HEADERS, params={"order": "added_at.desc", "limit": limit})
        return r.json()


async def get_pending_reports(limit=50):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE}/pending_reports", headers=HEADERS, params={"status": "eq.pending", "order": "submitted_at", "limit": limit})
        return r.json()


async def delete_from_scam_base(record_id: int):
    async with httpx.AsyncClient() as client:
        await client.delete(f"{BASE}/scam_base", headers=HEADERS, params={"id": f"eq.{record_id}"})


async def log_search(user_id: int, query: str, found: bool):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{BASE}/search_logs", headers=HEADERS, json={"searched_by": user_id, "query": query, "found": found})
    except:
        pass
