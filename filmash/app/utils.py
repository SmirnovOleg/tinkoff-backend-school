import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.config import PAGE_SIZE
from app.db.models import User
from app.db.utils import get_session

security = HTTPBasic()


def get_hashed_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def auth(
    credentials: HTTPBasicCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> int:
    user = session.query(User).filter_by(login=credentials.username).first()
    correct_username = user.login if user else None
    correct_password = (
        bcrypt.checkpw(credentials.password.encode(), user.hashed_password.encode())
        if user
        else None
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect login or password',
            headers={'WWW-Authenticate': 'Basic'},
        )

    return user.id


def get_and_check_total_pages(page: int, total_items: int, page_size: int) -> int:
    total_pages = (total_items - 1) // page_size + 1 if total_items != 0 else 1
    if page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f'Page number = {page} must be less than '
            f'total number of pages = {total_pages}',
        )
    return total_pages


def get_page_size() -> int:
    return PAGE_SIZE
