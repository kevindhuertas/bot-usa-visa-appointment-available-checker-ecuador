import os
from pymongo import response
from supabase import create_client, Client
from page_credentials import SUPABASE_URL, SUPABASE_KEY


# Placeholder credentials
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Generic CRUD operations
def create_record(table_name: str, data: dict):
    supabase = get_supabase_client()
    return supabase.table(table_name).insert(data).execute()

def read_records(table_name: str, filters: dict = None):
    supabase = get_supabase_client()
    query = supabase.table(table_name).select("*")
    if filters:
        for key, value in filters.items():
            query = query.eq(key, value)
    return query.execute()

def update_record(table_name: str, match_column: str, match_value, data: dict):
    supabase = get_supabase_client()
    return supabase.table(table_name).update(data).eq(match_column, match_value).execute()

def delete_record(table_name: str, match_column: str, match_value):
    supabase = get_supabase_client()
    return supabase.table(table_name).delete().eq(match_column, match_value).execute()

def check_connection():
    try:
        supabase = get_supabase_client()
        # Just a simple query to check connection
        supabase.table("users").select("*").limit(1).execute()
        print(response)
        return True
    except Exception as e:
        print(f"Supabase connection check failed: {e}")
        return False
