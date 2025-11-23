import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / 'logs'
DOWNLOADS_DIR = BASE_DIR / 'downloads'
LOGS_DIR.mkdir(exist_ok=True)
DOWNLOADS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / 'parser.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

TARGET_URL = ('https://yandex.ru/maps/?ll=38.830636%2C48.471223&mode=poi&poi'
              '%5Bpoint%5D=38.830193%2C48.471345&poi%5Buri%5D=ymapsbm1%3A%2F%2'
              'Forg%3Foid%3D175874439005&tab=reviews&z=18.8')
