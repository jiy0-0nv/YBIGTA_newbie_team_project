from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from app.user.user_router import user
from app.review.review_router import router as preprocess_router
from app.config import PORT

from database.mysql_connection import engine
from app.user.user_repository import Base

# 데이터베이스에 users 테이블이 없으면 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# 유저 API: /api/user/*
app.include_router(user, prefix="/api/user")
# 전처리 API: /review/*
app.include_router(preprocess_router, prefix="/review")

if __name__=="__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
