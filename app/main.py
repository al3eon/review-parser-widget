from typing import Optional

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from core.config import STATIC_DIR

from .database import Base, SessionLocal, engine
from .models import Review
from .schemas import ReviewResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Review Widget API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')


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
        source: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """
    Возвращает список отзывов, отсортированных по дате (сначала новые).
    """
    query = db.query(Review)

    if source in ['vk', 'yandex']:
        query = query.filter(Review.source == source)

    reviews = (
        query
        .order_by(Review.date_original.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    for review in reviews:
        if review.avatar_filename:
            full_url = (str(request.base_url) +
                        'static/avatars/' + review.avatar_filename)
            review.avatar_filename = full_url
    return reviews

@app.get('/api/reviews/stats')
def get_reviews_stats(db: Session = Depends(get_db)):
    total_count = db.query(Review).count()
    vk_count = db.query(Review).filter(Review.source == 'vk').count()
    yandex_count = db.query(Review).filter(Review.source == 'yandex').count()
    return {
        'total': total_count,
        'vk': vk_count,
        'yandex': yandex_count
    }
