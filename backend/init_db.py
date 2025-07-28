from sqlalchemy import create_engine
from app.core.database import Base
from app.core.config import settings
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.database_url)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin_user:
        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        db.commit()
        print("Default admin user created: admin@example.com / admin123")
    
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")