import os
import re
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi_csrf_protect import CsrfProtect
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
from utils.file_utils import (
    delete_cover_from_cloudinary,
    validate_and_save_cover,
    validate_cover_url,
)

DEFAULT_COVER_PATH = "static/covers/default.jpg"

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
@router.head("/", response_class=HTMLResponse)
def read_books_page(
    request: Request,
    csrf_protect: Annotated[CsrfProtect, Depends()],
    user: Annotated[User, Depends(get_authenticated_user)],
):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": {"username": user.username, "is_admin": user.username in settings.admin_users},
            "csrf_token": csrf_token,
        },
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.get("/books-data")
def books_data(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    title: Annotated[str | None, Query()] = None,
    author: Annotated[str | None, Query()] = None,
    isbn: Annotated[str | None, Query()] = None,
    publisher: Annotated[str | None, Query()] = None,
    location: Annotated[str | None, Query()] = None,
    sort_by: Annotated[str, Query()] = "id",
    sort_order: Annotated[str, Query()] = "asc",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
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
            ((Book.isbn == "N/A") | (Book.isbn == ""), null()),
            else_=func.regexp_replace(Book.isbn, r"X$", ""),
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

    order_criteria.append(asc(Book.id))

    books = query.order_by(*order_criteria).offset(offset).limit(limit + 1).all()
    has_more = len(books) > limit
    books = books[:limit]

    books_data = [
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "isbn": b.isbn,
            "publisher": b.publisher,
            "location": b.location,
            "cover_path": b.cover_path,
            "description": b.description,
            "language": b.language,
            "personal_comment": b.personal_comment,
        }
        for b in books
    ]

    return JSONResponse(
        content={"books": books_data, "has_more": has_more},
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


class AddBookForm:
    def __init__(
        self,
        title: Annotated[str, Form(...)],
        author: Annotated[str, Form(...)],
        location: Annotated[str, Form(...)],
        isbn: Annotated[str, Form()] = "",
        publisher: Annotated[str, Form()] = "",
        description: Annotated[str | None, Form()] = None,
        language: Annotated[str, Form()] = "",
        personal_comment: Annotated[str | None, Form()] = None,
        cover: Annotated[UploadFile | None, File()] = None,
        cover_url: Annotated[str | None, Form()] = None,
    ):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publisher = publisher
        self.location = location
        self.description = description
        self.language = language
        self.personal_comment = personal_comment
        self.cover = cover
        self.cover_url = cover_url


@router.post("/add", response_class=HTMLResponse)
async def add_book(
    request: Request,
    csrf_protect: Annotated[CsrfProtect, Depends()],
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    form_data: Annotated[AddBookForm, Depends()],
):
    await csrf_protect.validate_csrf(request)

    isbn_canonical, location_cleaned, language_cleaned = _validate_book_fields(
        form_data.isbn, form_data.location, form_data.language
    )

    if form_data.cover_url:
        cover_path = validate_cover_url(form_data.cover_url)
    elif form_data.cover and form_data.cover.filename:
        cover_path = validate_and_save_cover(form_data.cover)
    else:
        cover_path = "static/covers/default.jpg"

    book = Book(
        title=form_data.title.strip(),
        author=form_data.author.strip(),
        isbn=isbn_canonical,
        publisher=form_data.publisher.strip(),
        location=location_cleaned,
        cover_path=cover_path,
        description=form_data.description.strip() if form_data.description else None,
        language=language_cleaned,
        personal_comment=form_data.personal_comment.strip() if form_data.personal_comment else None,
        owner=user,
    )

    crud_add_book(db, book)

    referer = request.headers.get("referer")
    if referer:
        return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


def _validate_book_fields(isbn: str, location: str, language: str | None):
    isbn_canonical = canonical(isbn.strip())
    if isbn_canonical and not (is_isbn13(isbn_canonical) or is_isbn10(isbn_canonical)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ISBN non valido. Deve essere un ISBN-13 corretto.",
        )

    location_cleaned = location.strip()
    if not re.fullmatch(r"[A-Z]+\d+", location_cleaned):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato location non valido. Deve essere lettere maiuscole seguite da cifre, es. A5",
        )

    language_cleaned = None
    if language:
        language_cleaned = language.strip().upper()
        if not re.fullmatch(r"[A-Z]{2,3}", language_cleaned):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lingua non valida. Deve essere 2-3 lettere maiuscole (es. IT, EN)",
            )

    return isbn_canonical, location_cleaned, language_cleaned


def _delete_old_cover(cover_path: str):
    if cover_path == DEFAULT_COVER_PATH:
        return

    if cover_path.startswith("https://res.cloudinary.com/"):
        delete_cover_from_cloudinary(cover_path)
    elif os.path.exists(cover_path):
        os.remove(cover_path)


class EditBookForm:
    def __init__(
        self,
        book_id: Annotated[int, Form(...)],
        title: Annotated[str, Form(...)],
        author: Annotated[str, Form(...)],
        location: Annotated[str, Form(...)],
        isbn: Annotated[str, Form()] = "",
        publisher: Annotated[str, Form()] = "",
        description: Annotated[str, Form()] = "",
        language: Annotated[str, Form()] = "",
        personal_comment: Annotated[str, Form()] = "",
        cover: Annotated[UploadFile | None, File()] = None,
    ):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publisher = publisher
        self.location = location
        self.description = description
        self.language = language
        self.personal_comment = personal_comment
        self.cover = cover


@router.post("/edit", response_class=HTMLResponse)
async def edit_book(
    request: Request,
    csrf_protect: Annotated[CsrfProtect, Depends()],
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    form_data: Annotated[EditBookForm, Depends()],
):
    await csrf_protect.validate_csrf(request)

    book = db.query(Book).filter(Book.id == form_data.book_id, Book.user_id == user.id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Libro non trovato")

    isbn_canonical, location_cleaned, language_cleaned = _validate_book_fields(
        form_data.isbn, form_data.location, form_data.language
    )

    book.title = form_data.title.strip()
    book.author = form_data.author.strip()
    book.isbn = isbn_canonical
    book.publisher = form_data.publisher.strip()
    book.location = location_cleaned
    book.description = form_data.description.strip()
    book.language = language_cleaned
    book.personal_comment = form_data.personal_comment.strip()

    if form_data.cover and form_data.cover.filename:
        new_cover = validate_and_save_cover(form_data.cover)
        _delete_old_cover(book.cover_path)
        book.cover_path = new_cover

    db.commit()

    referer = request.headers.get("referer")
    if referer:
        return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/delete", response_class=HTMLResponse)
async def delete_book(
    request: Request,
    csrf_protect: Annotated[CsrfProtect, Depends()],
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    book_id: Annotated[int, Form(...)],
):
    await csrf_protect.validate_csrf(request)

    book = db.query(Book).filter(Book.id == book_id, Book.user_id == user.id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro non trovato")

    if book.cover_path != DEFAULT_COVER_PATH:
        if book.cover_path.startswith("https://res.cloudinary.com/"):
            delete_cover_from_cloudinary(book.cover_path)
        elif os.path.exists(book.cover_path):
            os.remove(book.cover_path)

    crud_delete_book(db, book)

    referer = request.headers.get("referer")
    if referer:
        return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
