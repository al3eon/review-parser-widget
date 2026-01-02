import os
from typing import Optional

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.config import ALLOWED_ORIGINS, STATIC_DIR
from core.utils import log_and_alert

from .database import Base, SessionLocal, engine
from .models import Review
from .schemas import ReviewResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Review Widget API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ['*'] else ['*'],
    allow_credentials=True,
    allow_methods=['GET', 'OPTIONS'],
    allow_headers=['*'],
)


@app.middleware('http')
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        await log_and_alert(exc, f'Путь: {request.url.path}')
        return JSONResponse(
            status_code=500,
            content={'detail': 'Internal Server Error'}
        )

app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')


def get_db():
    """Генератор сессии базы данных (Dependency Injection)."""
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
    """Возвращает список отзывов, отсортированных по дате (сначала новые)."""
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
    """Возвращает статистику по количеству отзывов."""
    stats = db.query(
        Review.source,
        func.count().label('count')
    ).group_by(Review.source).all()

    total = sum(row.count for row in stats)
    result = {'total': total}
    for row in stats:
        result[row.source] = row.count
    return result


@app.get('/api/config/sources')
def get_sources_config():
    """Конфигурация источников отзывов (только URL меняются в .env)"""
    return {
        'vk': {
            'url': os.getenv('VK_TARGET'),
            'color': '#0077FF',
            'iconPath': '/static/icons/vk.svg',
            'displayName': 'ВКонтакте',
            'sourceName': 'VK'
        },
        'yandex': {
            'url': os.getenv('YA_TARGET'),
            'color': '#FC3F1D',
            'iconPath': '/static/icons/yandex.svg',
            'displayName': 'Яндекс',
            'sourceName': 'Яндекса'
        }
    }