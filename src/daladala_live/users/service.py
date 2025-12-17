import uuid
from sqlalchemy import select
from daladala_live.core.database import database
from .models import User
from daladala_live.core.security import hash_password
from daladala_live.utils import generate_public_id  # the function above


async def create_user(email: str, password: str):
    public_id = generate_public_id()

    query = User.__table__.insert().values(
        email=email,
        hashed_password=hash_password(password),
        is_active=True,
        public_id=public_id,
    )
    await database.execute(query)

    return {
        "public_id": public_id,
        "email": email,
        "is_active": True,
    }


async def get_user_by_email(email: str):
    query = User.__table__.select().where(User.email == email)
    return await database.fetch_one(query)
