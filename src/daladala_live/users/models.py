# daladala_live/users/models.py
from sqlalchemy import Column, Integer, String, Boolean
from daladala_live.core.database import Base
from daladala_live.utils import generate_public_id  # the function above


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    public_id = Column(
        String(11), unique=True, nullable=False, default=generate_public_id
    )
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
