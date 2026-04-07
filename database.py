import json
import os
import aiofiles
from dotenv import load_dotenv

load_dotenv()

# Toggle this to True when you have added your Supabase credentials to .env
USE_SUPABASE = os.getenv("USE_SUPABASE", "False") == "True"
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if USE_SUPABASE:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

REMINDER_FILE = "data/reminder.json"
VERSIONS_FILE = "data/versions.json"


# ==========================================
# REMINDERS
# ==========================================

async def load_reminders() -> list:
    """Async loads reminders from Supabase or JSON"""
    if USE_SUPABASE:
        # -- Supabase migration boilerplate --
        # response = supabase.table("reminders").select("*").execute()
        # return response.data
        pass
    
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
        # -- Supabase migration boilerplate --
        # For supabase, you usually insert/delete individually,
        # but to keep it simple during migration, you could upsert the list
        # or recreate the table if needed.
        pass
    
    # JSON Fallback
    os.makedirs(os.path.dirname(REMINDER_FILE), exist_ok=True)
    async with aiofiles.open(REMINDER_FILE, "w") as f:
        await f.write(json.dumps({"reminders": reminders_list}, indent=4))


# ==========================================
# VERSIONS / RELEASES
# ==========================================

async def get_latest_release():
    """Async fetches the latest release from Supabase or JSON"""
    if USE_SUPABASE:
        # -- Supabase migration boilerplate --
        # response = supabase.table("versions").select("*").order("timestamp", desc=True).limit(1).execute()
        # return response.data[0] if response.data else None
        pass

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
    if USE_SUPABASE:
        # -- Supabase migration boilerplate --
        # supabase.table("versions").insert(release_data).execute()
        pass

    # JSON Fallback
    os.makedirs(os.path.dirname(VERSIONS_FILE), exist_ok=True)
    file_data = {"releases": []}
    
    if os.path.exists(VERSIONS_FILE):
        try:
            async with aiofiles.open(VERSIONS_FILE, "r") as f:
                content = await f.read()
                file_data = json.loads(content)
        except Exception:
            pass
            
    if "releases" not in file_data:
        file_data["releases"] = []
        
    file_data["releases"].append(release_data)
    
    async with aiofiles.open(VERSIONS_FILE, "w") as f:
        await f.write(json.dumps(file_data, indent=4))
