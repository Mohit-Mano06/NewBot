import json
import os
import aiofiles
import aiohttp
from dotenv import load_dotenv

load_dotenv()

# Toggle this to True when you have added your Supabase credentials to .env
USE_SUPABASE = os.getenv("USE_SUPABASE", "False") == "True"
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

REMINDER_FILE = "data/reminder.json"
VERSIONS_FILE = "data/versions.json"


async def supabase_request(method, endpoint, data=None, extra_headers=None):
    if not USE_SUPABASE:
        return None
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    if extra_headers:
        headers.update(extra_headers)
        
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(method, url, headers=headers, json=data) as resp:
                if resp.status >= 300:
                    print(f"Supabase error ({resp.status}): {await resp.text()}")
                    return None
                
                # Some requests (like empty POSTs) might not return JSON
                text = await resp.text()
                if not text:
                    return []
                return json.loads(text)
        except Exception as e:
            print(f"Supabase connection error: {e}")
            return None


async def check_supabase_connection():
    """Checks if we can hit the REST API and the bot_data table exists."""
    if not USE_SUPABASE:
        return False
    # Just try to fetch 1 row from bot_data
    res = await supabase_request("GET", "bot_data?select=key&limit=1")
    return res is not None


# ==========================================
# REMINDERS
# ==========================================

async def load_reminders() -> list:
    """Async loads reminders from Supabase or JSON"""
    if USE_SUPABASE:
        res = await supabase_request("GET", "bot_data?key=eq.reminders&select=value")
        if res and len(res) > 0:
            return res[0].get("value", {}).get("reminders", [])
        return []
    
    # JSON Fallback
    if not os.path.exists(REMINDER_FILE):
        return []
    
    try:
        async with aiofiles.open(REMINDER_FILE, "r") as f:
            content = await f.read()
            if not content.strip():
                return []
            return json.loads(content).get("reminders", [])
    except Exception as e:
        print(f"Error loading reminders: {e}")
        return []

async def save_reminders(reminders_list: list):
    """Async saves reminders to Supabase or JSON"""
    if USE_SUPABASE:
        payload = {"key": "reminders", "value": {"reminders": reminders_list}}
        # Upsert config: Merge duplicates means it will update existing row if key exists
        await supabase_request("POST", "bot_data", data=payload, extra_headers={"Prefer": "resolution=merge-duplicates"})
    
    # Always keep JSON updated as a backup!
    os.makedirs(os.path.dirname(REMINDER_FILE), exist_ok=True)
    async with aiofiles.open(REMINDER_FILE, "w") as f:
        await f.write(json.dumps({"reminders": reminders_list}, indent=4))


# ==========================================
# VERSIONS / RELEASES
# ==========================================

async def get_latest_release():
    """Async fetches the latest release from Supabase or JSON"""
    if USE_SUPABASE:
        res = await supabase_request("GET", "bot_data?key=eq.versions&select=value")
        if res and len(res) > 0:
            releases = res[0].get("value", {}).get("releases", [])
            return releases[-1] if releases else None
        return None

    if not os.path.exists(VERSIONS_FILE):
        return None
        
    try:
        async with aiofiles.open(VERSIONS_FILE, "r") as f:
            content = await f.read()
            data = json.loads(content)
            releases = data.get("releases", [])
            return releases[-1] if releases else None
    except Exception as e:
        print(f"Error loading latest release: {e}")
        return None

async def save_release(release_data: dict):
    """Async saves a new release to Supabase or JSON"""
    # Fetch existing from wherever we are loading it
    file_data = {"releases": []}
    
    if USE_SUPABASE:
        res = await supabase_request("GET", "bot_data?key=eq.versions&select=value")
        if res and len(res) > 0:
             file_data = res[0].get("value", {"releases": []})
    elif os.path.exists(VERSIONS_FILE):
        try:
            async with aiofiles.open(VERSIONS_FILE, "r") as f:
                content = await f.read()
                file_data = json.loads(content)
        except Exception:
            pass
            
    if "releases" not in file_data:
        file_data["releases"] = []
        
    file_data["releases"].append(release_data)

    if USE_SUPABASE:
        payload = {"key": "versions", "value": file_data}
        await supabase_request("POST", "bot_data", data=payload, extra_headers={"Prefer": "resolution=merge-duplicates"})
    
    # Always update local JSON as backup
    os.makedirs(os.path.dirname(VERSIONS_FILE), exist_ok=True)
    async with aiofiles.open(VERSIONS_FILE, "w") as f:
        await f.write(json.dumps(file_data, indent=4))
