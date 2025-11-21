from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Football Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .auth import router as auth_router
from .weeks import router as weeks_router
from .picks import router as picks_router
from .leaderboard import router as leaderboard_router

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(weeks_router, prefix="/weeks", tags=["weeks"])
app.include_router(picks_router, prefix="/picks", tags=["picks"])
app.include_router(leaderboard_router, prefix="/leaderboard", tags=["leaderboard"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Football Predictor API"}
