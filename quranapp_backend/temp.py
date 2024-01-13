from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Define SQLAlchemy model for storing tokens
class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    access_token = Column(String)
    refresh_token = Column(String)
    access_token_expires = Column(DateTime)
    refresh_token_expires = Column(DateTime)

# Initialize FastAPI app
app = FastAPI()

# Generate secret key for encoding and decoding tokens
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Create a function to generate access tokens
def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Create a function to generate refresh tokens
def create_refresh_token(user_id: int, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    encoded_jwt = jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# A Sample user model
class User(BaseModel):
    username: str
    password: str

# Sample user data (in a real-world scenario, you would authenticate against a user database)
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "password": "testpassword"
    }
}

# Sample authentication endpoint
@app.post("/login")
async def login(user: User):
    if user.username in fake_users_db and fake_users_db[user.username]["password"] == user.password:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(user_id=1, expires_delta=refresh_token_expires)

        # Store access and refresh tokens in the database
        db_token = Token(user_id=1, access_token=access_token, refresh_token=refresh_token,
                         access_token_expires=datetime.utcnow() + access_token_expires,
                         refresh_token_expires=datetime.utcnow() + refresh_token_expires)
        db = SessionLocal()
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return {"access_token": access_token, "refresh_token": refresh_token}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.post("/refresh-token")
async def refresh_token(refresh_token: str):
    # Verify the refresh token
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        # Use the user_id to determine the user's data from the database
        # (In a real-world scenario, you would look up the user's data from the database based on the user_id)
        # Here we use a placeholder way, which assumes that the user_id is known and goes directly to refreshing the token
        token = SessionLocal().query(Token).filter(Token.user_id == user_id, Token.refresh_token == refresh_token).first()
        if token:
            if token.refresh_token_expires > datetime.utcnow():
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(data={"sub": token.user_id}, expires_delta=access_token_expires)
                return {"access_token": access_token}
            else:
                raise HTTPException(status_code=400, detail="Refresh token has expired")
        else:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Expired refresh token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid refresh token")