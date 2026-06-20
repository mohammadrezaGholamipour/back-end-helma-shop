from app.db.session import SessionLocal
from app.models import User, Store


def create_missing_stores():
    db = SessionLocal()

    users = db.query(User).all()

    created = 0

    for user in users:
        store = db.query(Store).filter(Store.owner_id == user.id).first()

        if not store:
            new_store = Store(owner_id=user.id)
            db.add(new_store)
            created += 1

    db.commit()
    db.close()

    print(f"{created} stores created")
