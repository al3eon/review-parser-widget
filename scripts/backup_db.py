import asyncio
import datetime
import os
import sqlite3
import zipfile

from core.config import BACKUP_DIR, DB_PATH, TG_CHAT_ID
from core.logger import bot, logger, send_telegram_file, send_telegram_message

os.makedirs(BACKUP_DIR, exist_ok=True)


async def backup_process():
    """Создает hot-backup SQLite, сжимает и отправляет в ТГ."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'backup_{timestamp}.db')
    zip_file = f'{backup_file}.zip'

    logger.info(f'Запуск создания резервной копии: {DB_PATH} -> {backup_file}')

    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, _perform_sqlite_backup, DB_PATH, backup_file
        )

    except Exception as e:
        err_msg = f'Ошибка при создании резервной копии: {e}'
        logger.error(err_msg)
        await send_telegram_message(err_msg)
        return

    try:
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(backup_file, os.path.basename(backup_file))

        os.remove(backup_file)
        logger.info(f'Резервная копия сжата: {zip_file}')

        if bot and TG_CHAT_ID:
            await send_telegram_file(
                zip_file, caption=f'Backup базы данных: {timestamp}'
            )
        else:
            logger.warning('Бот не подключен. '
                           'Резервная копия сохранена, но не отправлена.')

    except Exception as e:
        logger.error(f'Ошибка сжатия/отправки сообщения: {e}')

    _cleanup_old_backups()


def _perform_sqlite_backup(src_path, dst_path):
    """Синхронная функция для выполнения backup()"""
    if not os.path.exists(src_path):
        raise FileNotFoundError(f'База данных не найдена: {src_path}')

    src = sqlite3.connect(src_path)
    dst = sqlite3.connect(dst_path)
    with dst:
        src.backup(dst)
    dst.close()
    src.close()


def _cleanup_old_backups():
    """Удаляет файлы старше 7 дней (или > 7 штук)."""
    files = sorted(
        [os.path.join(BACKUP_DIR, f)
         for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')],
        key=os.path.getmtime
    )
    while len(files) > 7:
        old_file = files.pop(0)
        try:
            os.remove(old_file)
            logger.info(f'Удаление старых резервных копий: {old_file}')
        except OSError as e:
            logger.error(f'Ошибка при удалении старых резервных копий: '
                         f'{old_file}: {e}')
