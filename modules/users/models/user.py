from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from conf.database.base import Base


class User(Base):
    """Represents an application user account."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        sa.BigInteger, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(sa.String(255))
    first_name: Mapped[str | None] = mapped_column(sa.String(100), default=None)
    last_name: Mapped[str | None] = mapped_column(sa.String(100), default=None)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, server_default=sa.true()
    )
    is_superuser: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, server_default=sa.false()
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"
