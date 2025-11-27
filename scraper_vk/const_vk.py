DIV_ALL_REVIE = ('xpath', '//div[@class="vkitReviewWrapper__root--Gi9Kt"]')

NAME = ('xpath', './/div[@class="vkitTextClamp__root--nWHhg '
                 'vkitTextClamp__rootSingleLine--7YAg4 '
                 'vkuiFootnote__host vkuiFootnote__sizeYCompact '
                 'vkuiTypography__host vkuiTypography__normalize '
                 'vkuiTypography__weight2 vkuiTypography__accent '
                 'vkuiRootComponent__host"]')

RATING = ('xpath', './/div[@class="vkitStar__root--4hbS9"]')

DATE_PUBLISH = ('xpath', './/span[@class="vkitgetColorClass__'
                         'colorTextSecondary--1ForK '
                         'vkuiFootnote__host vkuiFootnote__sizeYCompact '
                         'vkuiTypography__host vkuiTypography__normalize '
                         'vkuiTypography__inline vkuiRootComponent__host"]')

AVATAR = ('xpath', '(.//img[@class="vkuiImageBase__img '
                   'vkuiImageBase__imgObjectFitCover"])[1]')
FIRST_PHOTO = ('xpath', '(.//img[@class="vkuiImageBase__img '
                        'vkuiImageBase__imgObjectFitCover"])[2]')
TEXT_REVIEW = ('xpath', './/span[@class="vkuiFootnote__host '
                        'vkuiFootnote__sizeYCompact '
                        'vkuiTypography__host vkuiTypography__normalize '
                        'vkuiRootComponent__host"]')

LOOK_ALL_REVIEW = ('xpath', '//span[text()="Вы посмотрели все отзывы"]')

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36')

MAX_ATTEMPTS = 20
LOW_RATING = ['1', '2', '3']