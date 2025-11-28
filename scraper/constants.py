# Яндекс

YA_SORT_STATUS = ('xpath', '//span[text()="По умолчанию"]')
YA_SORT_BY_NEW = ('xpath', '//div[@aria-label="По новизне"]')
YA_DIV_ALL_REVIEWS = (
    'xpath',
    '//div[@class="business-reviews-card-view__review"]'
)
YA_AVATAR_LINK = ('xpath', './/div[@class="user-icon-view__icon"]')
YA_NAME = ('xpath', './/span[@itemprop="name"]')
YA_DATE_PUBLISH = ('xpath', './/meta[@itemprop="datePublished"]')
YA_RATING = (
    'xpath',
    './/div[@class="business-rating-badge-view__stars _spacing_normal"]'
)
YA_SPOILER_TEXT_BUTTON = ('xpath', './/span[text()="Ещё"]')
YA_REVIEW_TEXT = ('xpath', './/span[@class=" spoiler-view__text-container"]')
YA_CUSTOM_MONTH = {1: 'янв.', 2: 'фев.', 3: 'мар.', 4: 'апр.',
                   5: 'мая', 6: 'июн.', 7: 'июл.', 8: 'авг.',
                   9: 'сен.', 10: 'окт.', 11: 'ноя.', 12: 'дек.'}
# ВК

VK_LOGIN = ('xpath', '//span[text()="Войти другим способом"]')
VK_FIELD_NUMBER = ('xpath', '//input[@class="vkuiUnstyledTextField__host '
                            'vkuiInput__el vkuiText__host '
                            'vkuiText__sizeYCompact vkuiTypography__host '
                            'vkuiRootComponent__host"]')
VK_NUMBER_CONTINUE = ('xpath', '//span[text()="Войти"]')
VK_FIELD_PASSWORD = ('xpath', '//input[@aria-label="Введите пароль"]')
VK_PASSWORD_CONTINUE = ('xpath', '//span[@class="vkuiButton__in"]')

VK_DIV_ALL_REVIEWS = ('xpath', '//div[@class="vkitReviewWrapper__'
                               'root--Gi9Kt"]')
VK_MAX_ATTEMPTS = 20
VK_LOOK_ALL_REVIEW = ('xpath', '//span[text()="Вы посмотрели все отзывы"]')
VK_AVATAR_LINK = ('xpath', '(.//img[@class="vkuiImageBase__img '
                           'vkuiImageBase__imgObjectFitCover"])[1]')
VK_NAME = ('xpath', './/div[@class="vkitTextClamp__root--nWHhg '
                    'vkitTextClamp__rootSingleLine--7YAg4 '
                    'vkuiFootnote__host vkuiFootnote__sizeYCompact '
                    'vkuiTypography__host vkuiTypography__normalize '
                    'vkuiTypography__weight2 vkuiTypography__accent '
                    'vkuiRootComponent__host"]')
VK_RATING = ('xpath', './/div[@class="vkitStar__root--4hbS9"]')

VK_FIRST_PHOTO = ('xpath', '(.//img[@class="vkuiImageBase__img '
                           'vkuiImageBase__imgObjectFitCover"])[2]')
VK_TEXT_REVIEW = ('xpath', './/span[@class="vkuiFootnote__host '
                           'vkuiFootnote__sizeYCompact '
                           'vkuiTypography__host vkuiTypography__normalize '
                           'vkuiRootComponent__host"]')
VK_DATE_PUBLISH = ('xpath', './/span[@class="vkitgetColorClass__'
                            'colorTextSecondary--1ForK '
                            'vkuiFootnote__host vkuiFootnote__sizeYCompact '
                            'vkuiTypography__host vkuiTypography__normalize '
                            'vkuiTypography__inline vkuiRootComponent__host"]')
# Общие

LOW_RATING = ['1', '2', '3']
USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36')
