import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

from scraper.constants import USER_AGENT

load_dotenv()


def init_driver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(f'--user-agent={USER_AGENT}')
    selenium_url = os.getenv('SELENIUM_URL')

    if selenium_url:
        driver = webdriver.Remote(
            command_executor=selenium_url,
            options=options
        )
    else:
        driver = webdriver.Chrome(options=options)
        stealth(driver,
                languages=['ru-RU', 'ru'],
                vendor='Google Inc.',
                platform='Win32',
                webgl_vendor='Intel Inc.',
                renderer='Intel Iris OpenGL Engine',
                fix_hairline=True,
                )

    driver.set_window_size(1920, 1080)
    return driver
