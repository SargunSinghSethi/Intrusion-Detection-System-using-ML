from fastapi import Header, HTTPException, Depends
from typing import Optional
import jwt
import requests
from functools import lru_cache
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
import os

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "")

@lru_cache()
def get_jwks():
    """Cache JWKS keys from Clerk"""
    if not CLERK_JWKS_URL:
        return None
    try:
        response = requests.get(CLERK_JWKS_URL)
        return response.json()
    except:
        return None

def verify_clerk_token(authorization: Optional[str]) -> dict:
    """Verify Clerk JWT token or use stub for development"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")
    
    token = authorization.split("Bearer ")[-1].strip()
    
    # Development stub mode if no JWKS URL configured
    if not CLERK_JWKS_URL or CLERK_JWKS_URL == "":
        return {
            "clerk_user_id": token,
            "email": f"{token}@example.com",
            "name": token
        }
    
    try:
        # Production: Verify with Clerk JWKS
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        jwks = get_jwks()
        if not jwks:
            raise HTTPException(status_code=401, detail="Unable to verify token")
        
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Invalid token key")
        
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        
        return {
            "clerk_user_id": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get or create user from Clerk token"""
    clerk_data = verify_clerk_token(authorization)
    
    user = db.query(User).filter(
        User.clerk_user_id == clerk_data["clerk_user_id"]
    ).first()
    
    if not user:
        user = User(
            clerk_user_id=clerk_data["clerk_user_id"],
            email=clerk_data.get("email"),
            name=clerk_data.get("name")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user
