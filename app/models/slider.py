from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base


class Slider(Base):
    __tablename__ = "sliders"

    id = Column(Integer, primary_key=True)

    image = Column(String(500), nullable=False)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    display_order = Column(
        Integer,
        nullable=False,
        default=1,
    )
