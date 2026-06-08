from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    # id: Mapped[int] = mapped_column(
    #     INTEGER, nullable=False, unique=True, primary_key=True, autoincrement=True, index=True
    # )

    # created_at = mapped_column(TIMESTAMP, nullable=True, default=datetime.now)
    # updated_at = mapped_column(TIMESTAMP, nullable=True, default=datetime.now, onupdate=datetime.now)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
