from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from config import DOWNLOADS_DIR
from database import SessionLocal
from models import Review
from schemas import ReviewResponse

app = FastAPI(title='Review Widget API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static', StaticFiles(directory=DOWNLOADS_DIR), name='static')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/api/reviews', response_model=list[ReviewResponse])
def get_reviews(
        request: Request,
        limit: int = 6,
        offset: int = 0,
        db: Session = Depends(get_db)
):
    """
    Возвращает список отзывов, отсортированных по дате (сначала новые).
    """

    reviews = (
        db.query(Review)
        .order_by(Review.date_original.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    for review in reviews:
        if review.avatar_filename:
            full_url = (str(request.base_url) +
                        'static/' + review.avatar_filename)
            review.avatar_filename = full_url
    return reviews
