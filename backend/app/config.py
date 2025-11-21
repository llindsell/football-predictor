import os

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"postgresql://{os.environ.get('USER')}@localhost:5432/football_predictor")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID")

settings = Settings()
