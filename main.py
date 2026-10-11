import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = FastAPI(title="Auth API", description="FastAPI API with Supabase authentication", version="1.0.0")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Server running and connected to Supabase")

class Credentials(BaseModel):
    email: str
    password: str


@app.post("/auth/signup", status_code=201, summary="Create a new user account")
async def signup(creds: Credentials):
    if not creds.email.strip() or not creds.password.strip():
        raise HTTPException(status_code=400, detail="Email and password are required")
    try:
        response = supabase.auth.sign_up({"email": creds.email, "password": creds.password})
        return {"user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", summary="Log in and receive an access token")
async def login(creds: Credentials):
    if not creds.email.strip() or not creds.password.strip():
        raise HTTPException(status_code=400, detail="Email and password are required")
    try:
        response = supabase.auth.sign_in_with_password({"email": creds.email, "password": creds.password})
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")