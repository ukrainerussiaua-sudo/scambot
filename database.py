from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def check_scam_by_id(telegram_id: int):
    res = supabase.table("scam_base").select("*").eq("telegram_id", telegram_id).execute()
    return res.data if res.data else None


async def check_scam_by_username(username: str):
    username = username.lower().lstrip("@")
    res = supabase.table("scam_base").select("*").ilike("username", username).execute()
    return res.data if res.data else None


async def check_scam_by_phone(phone: str):
    res = supabase.table("scam_base").select("*").eq("phone", phone).execute()
    return res.data if res.data else None


async def add_to_scam_base(data: dict):
    res = supabase.table("scam_base").insert(data).execute()
    return res.data


async def create_pending_report(data: dict):
    res = supabase.table("pending_reports").insert(data).execute()
    return res.data[0] if res.data else None


async def get_pending_report(report_id: int):
    res = supabase.table("pending_reports").select("*").eq("id", report_id).execute()
    return res.data[0] if res.data else None


async def update_report_status(report_id: int, status: str):
    supabase.table("pending_reports").update({"status": status}).eq("id", report_id).execute()


async def update_report_moderation_msg(report_id: int, msg_id: int):
    supabase.table("pending_reports").update({"moderation_message_id": msg_id}).eq("id", report_id).execute()


async def get_all_scammers(limit=50):
    res = supabase.table("scam_base").select("*").order("added_at", desc=True).limit(limit).execute()
    return res.data


async def get_pending_reports(limit=50):
    res = supabase.table("pending_reports").select("*").eq("status", "pending").order("submitted_at").limit(limit).execute()
    return res.data


async def delete_from_scam_base(record_id: int):
    supabase.table("scam_base").delete().eq("id", record_id).execute()


async def log_search(user_id: int, query: str, found: bool):
    try:
        supabase.table("search_logs").insert({
            "searched_by": user_id,
            "query": query,
            "found": found
        }).execute()
    except:
        pass
