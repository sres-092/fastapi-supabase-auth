import os
from fastapi import FastAPI, HTTPException, Header, Depends, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = FastAPI(title="Auth API", description="FastAPI API with Supabase authentication", version="1.0.0")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

bearer_scheme = HTTPBearer(auto_error=False)


def get_token(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Access token required")
    return credentials.credentials


def get_current_user(token: str = Depends(get_token)):
    try:
        response = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if response is None or response.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return response.user

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

@app.get("/public/info", summary="Public information — no login needed")
async def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile", summary="Private profile — requires a valid token")
async def profile(user = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "created_at": user.created_at}


@app.get("/protected/dashboard", summary="Private dashboard — requires a valid token")
async def dashboard(user = Depends(get_current_user)):
    return {"message": f"Welcome to your dashboard, {user.email}"}


@app.post("/auth/logout", status_code=204, summary="Log out and end the session")
async def logout(user = Depends(get_current_user), token: str = Depends(get_token)):
    try:
        supabase.auth.admin.sign_out(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return Response(status_code=204)