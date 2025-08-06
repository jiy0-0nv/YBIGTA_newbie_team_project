from typing import Optional

from sqlalchemy import Column, String, MetaData
from sqlalchemy.orm import Session, declarative_base

from database.mysql_connection import SessionLocal, engine

from app.user.user_schema import User

Base = declarative_base()
metadata = MetaData()

class UserModel(Base):
    __tablename__ = "users"
    email    = Column(String(255), primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)

class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
        # Base.metadata.create_all(bind=self.db.get_bind())

    def get_user_by_email(self, email: str) -> Optional[User]:
        obj = self.db.query(UserModel).filter(UserModel.email == email).first()
        if not obj:
            return None
        return User(
            email=obj.email,
            password=obj.password,
            username=obj.username,
        )

    def save_user(self, user: User) -> User: 
        obj = self.db.query(UserModel).filter(UserModel.email == user.email).first()
        if obj:
            # 기존 유저가 있으면 업데이트
            obj.password = user.password
            obj.username = user.username
        else:
            # 새 유저 생성
            obj = UserModel(
                email=user.email,
                password=user.password,
                username=user.username,
            )
            self.db.add(obj)

        self.db.commit()
        return User(
            email=obj.email,
            password=obj.password,
            username=obj.username,
        )

    def delete_user(self, user: User) -> User:
        obj = self.db.query(UserModel).filter(UserModel.email == user.email).first()
        if not obj:
            raise ValueError("User not found")
        self.db.delete(obj)
        self.db.commit()
        # 삭제 후 원본 Pydantic 모델 반환
        return user
    
# Base.metadata.create_all(bind=engine)