from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DIV_ALL_REVIEWS = (
    'xpath',
    '//div[@class="business-reviews-card-view__review"]'
)
NAME = ('xpath', './/span[@itemprop="name"]')
RATING = (
    'xpath',
    './/div[@class="business-rating-badge-view__stars _spacing_normal"]'
)
DATE_VAR = ('xpath', './/meta[@itemprop="datePublished"]')
REVIEW_TEXT = ('xpath', './/span[@class=" spoiler-view__text-container"]')
LINK = ('xpath', './/div[@class="user-icon-view__icon"]')
IMG = ('xpath', '//img')
CUSTOM_MONTH = {1: 'янв.', 2: 'фев.', 3: 'мар.', 4: 'апр.',
                5: 'мая', 6: 'июн.', 7: 'июл.', 8: 'авг.',
                9: 'сен.', 10: 'окт.', 11: 'ноя.', 12: 'дек.'}

SPOILER_TEXT_BUTTON = ('xpath', './/span[text()="Ещё"]')

SORT_STATUS = ('xpath', '//span[text()="По умолчанию"]')
SORT_BY_NEW = ('xpath', '//div[@aria-label="По новизне"]')
LOW_RATING = ['1', '2', '3']

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36')
