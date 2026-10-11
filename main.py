import os
from fastapi import FastAPI
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = FastAPI(title="Auth API", description="FastAPI API with Supabase authentication", version="1.0.0")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Server running and connected to Supabase")