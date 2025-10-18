from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.models.author_model import Author
from app.schemas.author_schema import AuthorResponse
from app.models.admin_model import Admin
from app.core.deps import get_current_admin,get_db
from app.utils.response import success_response, error_message
import os
import uuid

router = APIRouter(
    prefix="/admin/authors",
    tags=["Admin - Authors"],
    dependencies=[Depends(get_current_admin)]
)

UPLOAD_DIR = "uploads/author_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
def create_author(
    full_name: str = Form(...),
    biography: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    try:
        existing = db.query(Author).filter(Author.full_name == full_name).first()
        if existing:
            return error_message(400, "Author already exists")

        image_path = None
        if file:
            file_ext = os.path.splitext(file.filename)[1]
            file_name = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, file_name).replace("\\", "/")
            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())
            image_path = f"/{file_path}"

        new_author = Author(full_name=full_name, biography=biography, image=image_path)
        db.add(new_author)
        db.commit()
        db.refresh(new_author)

        return success_response("Author created successfully", {
            "id": new_author.id,
            "full_name": new_author.full_name,
            "biography": new_author.biography,
            "image": new_author.image
        })
    except Exception as e:
        return error_message(500, str(e))

# ✅ LIST AUTHORS
@router.get("/")
def list_authors(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    try:
        authors = db.query(Author).order_by(Author.created_at.desc()).all()
        return success_response("Authors fetched successfully", [
            {
                "id": a.id,
                "full_name": a.full_name,
                "biography": a.biography,
                "image": a.image,
                "created_at": a.created_at,
                "updated_at": a.updated_at
            } for a in authors
        ])
    except Exception as e:
        return error_message(500, str(e))

@router.get("/{author_id}")
def get_author(author_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    try:
        author = db.query(Author).filter(Author.id == author_id).first()
        if not author:
            return error_message(404, "Author not found")
        return success_response("Author fetched successfully", {
            "id": author.id,
            "full_name": author.full_name,
            "biography": author.biography,
            "image": author.image,
            "created_at": author.created_at,
            "updated_at": author.updated_at
        })
    except Exception as e:
        return error_message(500, str(e))

@router.put("/{author_id}")
def update_author(
    author_id: int,
    full_name: str = Form(None),
    biography: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    try:
        author = db.query(Author).filter(Author.id == author_id).first()
        if not author:
            return error_message(404, "Author not found")

        if full_name:
            author.full_name = full_name
        if biography:
            author.biography = biography
        if file:
            file_ext = os.path.splitext(file.filename)[1]
            file_name = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, file_name).replace("\\", "/")
            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())
            author.image = f"/{file_path}"

        db.commit()
        db.refresh(author)
        return success_response("Author updated successfully", {
            "id": author.id,
            "full_name": author.full_name,
            "biography": author.biography,
            "image": author.image
        })
    except Exception as e:
        return error_message(500, str(e))

@router.delete("/{author_id}")
def delete_author(author_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    try:
        author = db.query(Author).filter(Author.id == author_id).first()
        if not author:
            return error_message(404, "Author not found")

        if author.image and os.path.exists(author.image.strip("/")):
            os.remove(author.image.strip("/"))

        db.delete(author)
        db.commit()
        return success_response("Author deleted successfully")
    except Exception as e:
        return error_message(500, str(e))
