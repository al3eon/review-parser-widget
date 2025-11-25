# Review Widget Service
Микросервис для сбора и отображения отзывов с Яндекс.Карт.

## Описание
Проект состоит из двух независимых частей:

- Parser (Scraper) — Скрипт на Selenium. Заходит на страницу организации, собирает отзывы, скачивает аватарки и сохраняет данные в локальную БД (SQLite).

- API — Веб-сервер на FastAPI. Раздает сохраненные отзывы в JSON формате и статические файлы (аватарки, JS-виджет).

## Стек технологий
- Язык: Python 3.10+
- Web Framework: FastAPI 
- Database: SQLite (SQLAlchemy)
- Parsing: Selenium WebDriver (Chrome)
- Frontend Widget: Vanilla JS (встроен)


## Установка и запуск
### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd <repository>
```

### 2. Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv venv
```

- Если у вас Linux/macOS
    ```
    source venv/bin/activate
    ```
  
- Если у вас windows
    ```bash
    source venv/scripts/activate
    ```

### 3. Установить зависимости из файла requirements.txt:
```bash
pip install -r requirements.txt
```

### 4. Запуск Парсера
```bash
python -m scraper.main
```
Скрипт откроет браузер, соберет данные и закроется. Логи работы будут в data/logs/parser.log.

### 5. Запуск API
```bash
uvicorn app.main:app --reload
```
Сервер запустится по адресу: http://127.0.0.1:8000

### 6. Документация API: 
- [Swagger](http://127.0.0.1:8000/docs) 
- [ReDoc](http://localhost:8000/redoc)

### 7. Интеграция на сайт
Вставьте этот код в HTML страницы, где нужно вывести отзывы:
```
<div id="lev-lab"></div>
<script src="http://127.0.0.1:8000/static/widget.js"></script>
```