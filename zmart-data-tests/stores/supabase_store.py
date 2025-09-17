import os
from supabase import create_client, Client

SUPABASE_URL=os.getenv("SUPABASE_URL","")
SUPABASE_KEY=os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY","")

def client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Supabase config missing")
    return create_client(SUPABASE_URL, SUPABASE_KEY)
