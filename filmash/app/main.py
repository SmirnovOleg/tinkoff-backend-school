from datetime import datetime
from typing import Any, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Film, Review, User
from app.db.utils import get_session, init_db
from app.utils import (
    auth,
    get_and_check_total_pages,
    get_hashed_password,
    get_page_size,
)
from app.validators import (
    ReviewRequestBodyModel,
    ScoreRequestBodyModel,
    SortType,
    UserRequestBodyModel,
)

app = FastAPI()


@app.post('/users')
def register_new_user(
    body: UserRequestBodyModel, session: Session = Depends(get_session)
) -> Any:
    login, password = body.login, body.password

    if session.query(User).filter_by(login=login).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with specified login already exists',
        )

    hashed_password = get_hashed_password(password.get_secret_value())
    user = User(login=login, hashed_password=hashed_password)

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except IntegrityError as e:
        if session.query(User).filter_by(login=login).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='User with specified login already exists',
            ) from e

    return {'registered_login': user.login}


@app.post('/films/{film_id}/scores')
def post_new_score(
    film_id: int,
    body: ScoreRequestBodyModel,
    user_id: int = Depends(auth),
    session: Session = Depends(get_session),
) -> Any:
    score = body.score

    film = session.query(Film).get(film_id)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Film with specified id = {film_id} does not exist',
        )
    review = session.query(Review).filter_by(user_id=user_id, film_id=film.id).first()
    if not review:
        review = Review(user_id=user_id, film_id=film.id, score=score)
        try:
            session.add(review)
            film.total_scores += 1
            if film.avg_score:
                film.avg_score = (film.avg_score * film.total_scores + score) / (
                    film.total_scores + 1
                )
            else:
                film.avg_score = score
        except IntegrityError:
            # If somebody posted a review during our transaction, just update existing scores
            if (
                session.query(Review)
                .filter_by(user_id=user_id, film_id=film.id)
                .first()
            ):
                film.avg_score = (
                    film.avg_score * film.total_scores - review.score + score
                ) / (film.total_scores)
                review.score = score
    else:
        film.avg_score = (film.avg_score * film.total_scores - review.score + score) / (
            film.total_scores
        )
        review.score = score

    session.commit()
    session.refresh(review)

    return {
        'film_name': film.name,
        'posted_score': review.score,
        'avg_score': film.avg_score,
        'total_scores': film.total_scores,
    }


@app.get('/films/{film_id}/scores')
def get_scores_by_film(
    film_id: int,
    page: Optional[int] = Query(None, ge=1),
    _: int = Depends(auth),
    session: Session = Depends(get_session),
    page_size: int = Depends(get_page_size),
) -> Any:
    film = session.query(Film).get(film_id)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Film with specified id = {film_id} does not exist',
        )

    reviews_query = session.query(Review).filter(
        Review.film_id == film_id, Review.score.isnot(None)
    )
    total_pages = 1
    if page:
        total_scores = reviews_query.count()
        reviews_query = reviews_query.offset((page - 1) * page_size).limit(page_size)
        total_pages = get_and_check_total_pages(page, total_scores, page_size)

    return {
        'film_name': film.name,
        'avg_score': film.avg_score,
        'total_scores': film.total_scores,
        'scores': [
            {'user_id': review.user_id, 'score': review.score}
            for review in reviews_query.all()
        ],
        'page': page or 1,
        'total_pages': total_pages,
    }


@app.post('/films/{film_id}/comments')
def post_new_comment(
    film_id: int,
    body: ReviewRequestBodyModel,
    user_id: int = Depends(auth),
    session: Session = Depends(get_session),
) -> Any:
    comment = body.comment

    film = session.query(Film).get(film_id)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Film with specified id = {film_id} does not exist',
        )
    review = session.query(Review).filter_by(user_id=user_id, film_id=film.id).first()
    if not review:
        try:
            review = Review(user_id=user_id, film_id=film.id, comment=comment)
            session.add(review)
            film.total_comments += 1
        except IntegrityError:
            # If somebody posted a review during our transaction, just update existing scores
            if (
                session.query(Review)
                .filter_by(user_id=user_id, film_id=film.id)
                .first()
            ):
                review.comment = comment
    else:
        review.comment = comment

    session.commit()
    session.refresh(review)

    return {
        'film_name': film.name,
        'posted_comment': review.comment,
        'total_comments': film.total_comments,
    }


@app.get('/films/{film_id}/comments')
def get_comments_by_film(
    film_id: int,
    page: Optional[int] = Query(None, ge=1),
    _: int = Depends(auth),
    session: Session = Depends(get_session),
    page_size: int = Depends(get_page_size),
) -> Any:
    film = session.query(Film).get(film_id)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Film with specified id = {film_id} does not exist',
        )

    reviews_query = session.query(Review).filter(
        Review.film_id == film_id, Review.comment.isnot(None)
    )
    total_pages = 1
    if page:
        total_scores = reviews_query.count()
        reviews_query = reviews_query.offset((page - 1) * page_size).limit(page_size)
        total_pages = get_and_check_total_pages(page, total_scores, page_size)

    return {
        'film_name': film.name,
        'comments': [
            {'user_id': review.user_id, 'comment': review.comment}
            for review in reviews_query.all()
        ],
        'page': page or 1,
        'total_pages': total_pages,
    }


@app.get('/films/{film_id}')
def get_film_info(
    film_id: int, _: int = Depends(auth), session: Session = Depends(get_session)
) -> Any:
    film = session.query(Film).get(film_id)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Film with specified id = {film_id} does not exist',
        )

    return {
        'film_id': film.id,
        'film_name': film.name,
        'avg_score': film.avg_score,
        'total_scores': film.total_scores,
        'total_comments': film.total_comments,
    }


@app.get('/films')
def get_filtered_films(  # pylint: disable=too-many-arguments
    substring: Optional[str] = Query(None, max_length=100),
    year: Optional[int] = Query(None, ge=1895, le=datetime.now().year),
    sort_by_avg_score: Optional[SortType] = Query(None),
    top: Optional[int] = Query(None, ge=1),
    page: Optional[int] = Query(None, ge=1),
    session: Session = Depends(get_session),
    _: str = Depends(auth),
    page_size: int = Depends(get_page_size),
) -> Any:
    films_query = session.query(Film)

    if substring:
        films_query = session.query(Film).filter(Film.name.contains(substring))

    if year:
        films_query = films_query.filter_by(year=year)

    if sort_by_avg_score == SortType.ASC:
        films_query = films_query.order_by(Film.avg_score)
    elif sort_by_avg_score == SortType.DESC:
        films_query = films_query.order_by(Film.avg_score.desc())

    if top:
        films_query = films_query.limit(top)

    total_pages = 1
    if page:
        total_films = films_query.count()
        films_query = films_query.offset((page - 1) * page_size).limit(page_size)
        total_pages = get_and_check_total_pages(page, total_films, page_size)

    return {
        'films': [
            {
                'film_id': film.id,
                'film_name': film.name,
                'year': film.year,
                'avg_score': film.avg_score,
            }
            for film in films_query.all()
        ],
        'page': page or 1,
        'total_pages': total_pages,
    }


if __name__ == '__main__':
    init_db()
    uvicorn.run(app, host='0.0.0.0', port=8000)
