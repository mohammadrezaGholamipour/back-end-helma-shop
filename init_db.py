from app.models.category import Category
from app.models.product import Product
from app.db.session import engine
from app.models.user import User
from app.db.base import Base


Base.metadata.create_all(bind=engine)