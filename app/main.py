import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from core.config import ALLOWED_ORIGINS, STATIC_DIR
from core.scheduler import scheduler, start_scheduler
from core.utils import logger, send_telegram_message

from .database import Base, SessionLocal, engine
from .models import Review
from .schemas import ReviewResponse

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(title='Review Widget API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=['GET', 'OPTIONS'],
    allow_headers=['*'],
)


@app.middleware('http')
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f'Критическая ошибка: {exc}', exc_info=True)
        msg = f'Критическая ошибка!\n Путь: {request.url.path}\n Ошибка: {exc}'
        asyncio.create_task(send_telegram_message(msg))
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
    """Возвращает статистику по количеству отзывов."""
    total_count = db.query(Review).count()
    vk_count = db.query(Review).filter(Review.source == 'vk').count()
    yandex_count = db.query(Review).filter(Review.source == 'yandex').count()
    return {
        'total': total_count,
        'vk': vk_count,
        'yandex': yandex_count
    }
