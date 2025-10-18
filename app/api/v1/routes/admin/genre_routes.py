from app.models.admin_model import Admin
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_admin,get_db
from app.models.genre_model import Genre
from app.schemas.genre_schema import GenreCreate, GenreUpdate, GenreResponse
from app.utils.response import success_response,error_message

router = APIRouter(prefix="/admin/genres", tags=["Admin - Genres"],dependencies=[Depends(get_current_admin)])

@router.post("/")
def create_genre(genre: GenreCreate, db: Session = Depends(get_db),current_admin: Admin = Depends(get_current_admin)):
    try:
        existing_genre = db.query(Genre).filter(Genre.name == genre.name).first()
        if existing_genre:
            raise HTTPException(status_code=400, detail="Genre with this name already exists")

        new_genre = Genre(**genre.dict())
        db.add(new_genre)
        db.commit()
        db.refresh(new_genre)
        return success_response("Genre created successfully", {
            "id": new_genre.id,
            "name": new_genre.name,
            "description": new_genre.description
        })
    except Exception as e:
        return error_message(500, str(e))

@router.get("/")
def list_genres(db: Session = Depends(get_db),current_admin: Admin = Depends(get_current_admin)):
    try:
        genres = db.query(Genre).all()
        return success_response("Genres fetched successfully", genres)
    except Exception as e:
        return error_message(500, str(e))

@router.get("/{genre_id}")
def get_genre(genre_id: int, db: Session = Depends(get_db),current_admin: Admin = Depends(get_current_admin)):
    try:
        genre = db.query(Genre).filter(Genre.id == genre_id).first()
        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")
        return success_response("Genre fetched successfully", {
            "id": genre.id,
            "name": genre.name,
            "description": genre.description
        })
    except Exception as e:
        return error_message(500, str(e))

@router.put("/{genre_id}")
def update_genre(genre_id: int, genre_data: GenreUpdate, db: Session = Depends(get_db),current_admin: Admin = Depends(get_current_admin)):
    try:
        genre = db.query(Genre).filter(Genre.id == genre_id).first()
        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")

        for key, value in genre_data.dict(exclude_unset=True).items():
            setattr(genre, key, value)

        db.commit()
        db.refresh(genre)
        return success_response("Genre updated successfully", {
            "id": genre.id,
            "name": genre.name,
            "description": genre.description
        })
    except Exception as e:
        return error_message(500, str(e))

@router.delete("/{genre_id}")
def delete_genre(genre_id: int, db: Session = Depends(get_db),current_admin: Admin = Depends(get_current_admin)):
    try:
        genre = db.query(Genre).filter(Genre.id == genre_id).first()
        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")

        db.delete(genre)
        db.commit()
        return success_response("Genre deleted successfully")
    except Exception as e:
        return error_message(500, str(e))
