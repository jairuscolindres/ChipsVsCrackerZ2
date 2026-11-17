"""
Supabase client singleton for use across the Django project.

Usage:
    from config.supabase_client import supabase
    
    # Example: query a table
    response = supabase.table("my_table").select("*").execute()
    
    # Example: insert data
    response = supabase.table("my_table").insert({"key": "value"}).execute()
"""

import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
