from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.models.book_model import Book
from app.models.author_model import Author
from app.models.genre_model import Genre
from app.models.admin_model import Admin
from app.core.deps import get_current_admin, get_db
from app.utils.response import success_response, error_message
import uuid, os

UPLOAD_DIR = "uploads/book_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/admin/books", tags=["Admin - Books"], dependencies=[Depends(get_current_admin)])


@router.post("/")
def create_book(
    title: str = Form(...),
    author_id: int = Form(...),
    genre_id: int = Form(...),
    price: float = Form(...),
    stock: int = Form(0),
    description: str = Form(...),
    is_active: bool = Form(True),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    try:
        author = db.query(Author).filter(Author.id == author_id).first()
        genre = db.query(Genre).filter(Genre.id == genre_id).first()
        if not author or not genre:
            error_message(404, "Author or Genre not found")

        image_path = None
        if image:
            file_ext = os.path.splitext(image.filename)[1]
            file_name = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, file_name).replace("\\", "/")
            with open(file_path, "wb") as buffer:
                buffer.write(image.file.read())
            image_path = f"/{file_path}"

        new_book = Book(
            title=title,
            author_id=author_id,
            genre_id=genre_id,
            price=price,
            stock=stock,
            description=description,
            is_active=is_active,
            image=image_path,
        )
        db.add(new_book)
        db.commit()
        db.refresh(new_book)

        return success_response("Book created successfully", {
            "id": new_book.id,
            "title": new_book.title,
            "price": new_book.price,
            "stock": new_book.stock,
            "description": new_book.description,
            "is_active": new_book.is_active,
            "image": new_book.image,
            "author": author.full_name,
            "genre": genre.name
        })
    except Exception as e:
        return error_message(500, str(e))


@router.get("/")
def list_books(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    try:
        books = db.query(Book).all()
        result = []
        for b in books:
            author = db.query(Author).filter(Author.id == b.author_id).first()
            genre = db.query(Genre).filter(Genre.id == b.genre_id).first()
            result.append({
                "id": b.id,
                "title": b.title,
                "price": b.price,
                "stock": b.stock,
                "is_active": b.is_active,
                "image": b.image,
                "author": author.full_name if author else None,
                "genre": genre.name if genre else None
            })
        return success_response("Books fetched successfully", result)
    except Exception as e:
        return error_message(500, str(e))


@router.get("/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return success_response("Book fetched successfully", book.__dict__)
    except Exception as e:
        return error_message(500, str(e))


@router.put("/{book_id}")
def update_book(
    book_id: int,
    title: str = Form(...),
    author_id: int = Form(...),
    genre_id: int = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    description: str = Form(...),
    is_active: bool = Form(True),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        author = db.query(Author).filter(Author.id == author_id).first()
        genre = db.query(Genre).filter(Genre.id == genre_id).first()
        if not author or not genre:
            error_message(404, "Author or Genre not found")

        # Image update
        if image:
            file_ext = os.path.splitext(image.filename)[1]
            file_name = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, file_name).replace("\\", "/")
            with open(file_path, "wb") as buffer:
                buffer.write(image.file.read())
            book.image = f"/{file_path}"

        # Update fields
        book.title = title
        book.author_id = author_id
        book.genre_id = genre_id
        book.price = price
        book.stock = stock
        book.description = description
        book.is_active = is_active

        db.commit()
        db.refresh(book)

        return success_response("Book updated successfully", {
            "id": book.id,
            "title": book.title,
            "price": book.price,
            "stock": book.stock,
            "description": book.description,
            "is_active": book.is_active,
            "image": book.image,
            "author": author.full_name,
            "genre": genre.name
        })
    except Exception as e:
        return error_message(500, str(e))


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        db.delete(book)
        db.commit()
        return success_response("Book deleted successfully")
    except Exception as e:
        return error_message(500, str(e))