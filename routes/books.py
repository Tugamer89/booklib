import os
import re

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, status, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from isbnlib import canonical, is_isbn10, is_isbn13
from sqlalchemy import asc, case, cast, desc, func, null
from sqlalchemy.orm import Session
from sqlalchemy.types import BigInteger

from core.auth import get_authenticated_user
from core.config import settings
from core.templates import templates
from db.crud import add_book as crud_add_book, delete_book as crud_delete_book
from db.database import get_db
from db.models import Book, User
from utils.file_utils import validate_and_save_cover, validate_cover_url, delete_cover_from_cloudinary


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def read_books(
    request: Request,
    user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
    title: str = Query(None),
    author: str = Query(None),
    isbn: str = Query(None),
    publisher: str = Query(None),
    location: str = Query(None),
    sort_by: str = Query("id"),
    sort_order: str = Query("asc")
):
    query = db.query(Book).filter(Book.user_id == user.id)

    # Filtri
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if isbn:
        isbn_clean = isbn.replace("-", "").strip()
        query = query.filter(Book.isbn.ilike(f"%{isbn_clean}%"))
    if publisher:
        query = query.filter(Book.publisher.ilike(f"%{publisher}%"))
    if location:
        query = query.filter(Book.location.ilike(f"%{location}%"))

    # Ordinamento dinamico
    sort_column = getattr(Book, sort_by, Book.id)
    order_criteria = []

    if sort_by == "isbn":
        isbn_clean_col = case(
            ((Book.isbn == 'N/A') | (Book.isbn == ''), null()),
            else_=func.regexp_replace(Book.isbn, r'X$', '')
        )
        numeric_isbn = cast(isbn_clean_col, BigInteger)
        order_criteria.append(numeric_isbn)
    elif sort_column.property.columns[0].type.python_type is str:
        order_criteria.append(func.lower(sort_column))
    else:
        order_criteria.append(sort_column)

    if sort_order == "desc":
        order_criteria = [desc(c) for c in order_criteria]
    else:
        order_criteria = [asc(c) for c in order_criteria]

    query = query.order_by(*order_criteria)
    books = query.all()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "books": books,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "is_logged_in": True,
        "is_admin": user.username in settings.admin_users
    })


@router.post("/add", response_class=HTMLResponse)
def add_book(
    request: Request,
    user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    publisher: str = Form(...),
    location: str = Form(...),
    description: str = Form(None),
    language: str = Form(None),
    personal_comment: str = Form(None),
    cover: UploadFile = File(None),
    cover_url: str = Form(None),
):
    # Validazione ISBN
    isbn_canonical = canonical(isbn.strip())
    if isbn_canonical and not (is_isbn13(isbn_canonical) or is_isbn10(isbn_canonical)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ISBN non valido. Deve essere un ISBN-13 corretto.")

    # Validazione location
    if not re.fullmatch(r'[A-Z]+[0-9]+', location.strip()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato location non valido. Deve essere lettere maiuscole seguite da cifre (es. A5, AB30, LIBRERIA1)")

    # Validazione language
    if language:
        language = language.strip().upper()
        if not re.fullmatch(r'[A-Z]{2,3}', language):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lingua non valida. Deve essere 2-3 lettere maiuscole (es. IT, EN)")

    # Validazione e gestione cover
    if cover_url:
        cover_path = validate_cover_url(cover_url)
    elif cover and cover.filename:
        cover_path = validate_and_save_cover(cover)
    else:
        cover_path = "static/covers/default.jpg"

    # Creazione libro
    book = Book(
        title=title.strip(),
        author=author.strip(),
        isbn=isbn_canonical,
        publisher=publisher.strip(),
        location=location,
        cover_path=cover_path,
        description=description.strip(),
        language=language,
        personal_comment=personal_comment.strip(),
        owner=user
    )

    crud_add_book(db, book)

    referer = request.headers.get("referer")
    if referer:
        return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/edit", response_class=HTMLResponse)
def edit_book(
    request: Request,
    book_id: int = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    publisher: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    language: str = Form(...),
    personal_comment: str = Form(...),
    cover: UploadFile = File(None),
    user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.id == book_id, Book.user_id == user.id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Libro non trovato")

    # Validazione ISBN
    isbn_canonical = canonical(isbn.strip())
    if isbn_canonical and not (is_isbn13(isbn_canonical) or is_isbn10(isbn_canonical)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ISBN non valido. Deve essere un ISBN-13 corretto.")

    # Validazione location
    location = location.strip()
    if not re.fullmatch(r'[A-Z]+[0-9]+', location):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato location non valido. Deve essere lettere maiuscole seguite da cifre, es. A5")

    # Validazione language
    if language:
        language = language.strip().upper()
        if not re.fullmatch(r'[A-Z]{2,3}', language):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lingua non valida. Deve essere 2-3 lettere maiuscole (es. IT, EN)")

    book.title = title.strip()
    book.author = author.strip()
    book.isbn = isbn_canonical
    book.publisher = publisher.strip()
    book.location = location
    book.description = description.strip()
    book.language = language
    book.personal_comment = personal_comment.strip()

    if cover and cover.filename:
        new_cover = validate_and_save_cover(cover)
        if book.cover_path != "static/covers/default.jpg":
            if book.cover_path.startswith("https://res.cloudinary.com/"):
                delete_cover_from_cloudinary(book.cover_path)
            elif os.path.exists(book.cover_path):
                os.remove(book.cover_path)
        book.cover_path = new_cover

    db.commit()
    
    referer = request.headers.get("referer")
    if referer:
        return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/delete", response_class=HTMLResponse)
def delete_book(
    request: Request,
    book_id: int = Form(...),
    user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.id == book_id, Book.user_id == user.id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro non trovato")

    if book.cover_path != "static/covers/default.jpg":
        if book.cover_path.startswith("https://res.cloudinary.com/"):
            delete_cover_from_cloudinary(book.cover_path)
        elif os.path.exists(book.cover_path):
            os.remove(book.cover_path)

    crud_delete_book(db, book)
    
    referer = request.headers.get("referer")
    if referer:
        return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
