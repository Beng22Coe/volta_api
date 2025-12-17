from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from daladala_live.users.service import get_user_by_email
from daladala_live.core.security import verify_password, create_access_token
from daladala_live.users.schemas import UserCreate, UserOut
from daladala_live.users.service import create_user, get_user_by_email
from daladala_live.core.mailer import send_welcome_email

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register", response_model=UserOut)
async def register_user(payload: UserCreate):
    existing = await get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(payload.email, payload.password)
    return user

@router.post("/verify-email")
async def verify_email(token: str):
    # Here you would verify the token and activate the user's account
    return {"message": "Email verified successfully"}


@router.post("/login")
async def login(payload: LoginRequest):
    user = await get_user_by_email(payload.email)  # ✅ await here

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        subject=user.public_id
    )  # use public_id, not internal id

    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout_user():
    # In a real application, you might want to blacklist the token or handle logout differently
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_token(current_user: UserOut):
    new_token = create_access_token(subject=current_user.public_id)
    return {"access_token": new_token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password(email: str):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Here you would generate a password reset token and send it via email
    return {"message": "Password reset link sent to your email"}

@router.post("/reset-password")
async def reset_password(token: str, new_password: str):
    # Here you would verify the token and reset the user's password
    return {"message": "Password has been reset successfully"}
