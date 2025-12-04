import datetime
import os
import sqlite3
import zipfile

from core.config import BACKUP_DIR, DB_PATH, TG_CHAT_ID
from core.utils import bot, log_and_alert_sync, logger, send_telegram_file

os.makedirs(BACKUP_DIR, exist_ok=True)


def backup_process():
    """Создает hot-backup SQLite, сжимает и отправляет в ТГ."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'backup_{timestamp}.db')
    zip_file = f'{backup_file}.zip'

    logger.info(f'Запуск создания резервной копии: {DB_PATH} -> {backup_file}')

    try:
        src = sqlite3.connect(DB_PATH)
        dst = sqlite3.connect(backup_file)
        with dst:
            src.backup(dst)
        dst.close()
        src.close()
        logger.info('Бэкап БД создан успешно')

    except Exception as e:
        log_and_alert_sync(e, 'Ошибка создания резервной копии')
        return

    try:
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(backup_file, os.path.basename(backup_file))

        os.remove(backup_file)
        logger.info(f'Резервная копия сжата: {zip_file}')

        if bot and TG_CHAT_ID:
            try:
                import asyncio
                asyncio.create_task(
                    send_telegram_file(
                        zip_file, caption=f'Backup: {timestamp}'
                    )
                )
                logger.info('Файл отправлен в телеграм.')
            except Exception as e:
                logger.warning(f'Ошибка отправки в ТГ: {e}')
        else:
            logger.info('Бот не подключен или нет TG_CHAT_ID')

    except Exception as e:
        log_and_alert_sync(e, 'Ошибка сжатия резервной копии')

    _cleanup_old_backups()


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
            log_and_alert_sync(e, 'Ошибка при очистке старых бэкапов')


if __name__ == '__main__':
    backup_process()