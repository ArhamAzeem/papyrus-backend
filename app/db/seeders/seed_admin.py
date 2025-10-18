from app.db.session import SessionLocal, engine
from app.models.admin_model import Admin
from app.core.security import get_password_hash
from sqlalchemy.exc import IntegrityError

def seed_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        if not db.query(Admin).filter(Admin.email == "admin@example.com").first():
            admin = Admin(
                full_name="Super Admin",
                email="admin@example.com",
                password=get_password_hash("admin123")  # change password
            )
            db.add(admin)
            db.commit()
            print("Admin seeded successfully!")
        else:
            print("Admin already exists.")
    except IntegrityError as e:
        db.rollback()
        print("Error seeding admin:", str(e))
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
