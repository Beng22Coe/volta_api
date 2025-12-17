from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from daladala_live.users.service import get_user_by_email
from daladala_live.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(payload: LoginRequest):
    user = await get_user_by_email(payload.email)  # ✅ await here

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        subject=user.public_id
    )  # use public_id, not internal id

    return {"access_token": token, "token_type": "bearer"}
