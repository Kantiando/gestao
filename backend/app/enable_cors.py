from fastapi.middleware.cors import CORSMiddleware

from app.supabase_api import app

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gestao-front-wi4a.onrender.com",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
