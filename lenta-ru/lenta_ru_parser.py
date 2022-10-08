from selenium import webdriver
import requests
import re
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from csv import DictWriter

class DatetimeRange:
    def __init__(self, dt1, dt2):
        self._dt1 = dt1
        self._dt2 = dt2

    def __contains__(self, dt):
        return self._dt1 <= dt <= self._dt2

root = 'https://lenta.ru'
url = f'{root}/rubrics/economics/'
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

months = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12
}

def form_link_from_date(date_look: date):
    if date_look.day < 10:
        return f'{url}{date_look.year}/{date_look.month}/0{date_look.day}' 
    return f'{url}{date_look.year}/{date_look.month}/{date_look.day}'

def form_date_from_str(date_str: str):
    date_str = date_str.split(', ')[1]
    parts = date_str.split(' ')
    return date(int(parts[2]), months[parts[1]], int(parts[0]))

def get_article(link: str):
    driver.get(link)
    lxml = driver.page_source
    soup = BeautifulSoup(lxml, 'lxml')
    title = soup.find('span', class_='topic-body__title').get_text()
    date_pub_str = soup.find('time', class_='topic-header__item topic-header__time').get_text()
    date_pub = form_date_from_str(date_pub_str)
    unwanted = soup.find('div', class_='tradingview-widget-copyright')
    if unwanted is not None:
        unwanted.extract()
    content = soup.find('div', class_='topic-body__content').get_text().rstrip()
    num_comments = 0
    comments_count_tag = soup.find('span', class_='comments__count')
    if comments_count_tag is not None:
        num_comments_str = comments_count_tag.get_text()
        res = re.search(r"\((\d+)\)", num_comments_str)
        if res is not None:
            num_comments = int(res.group(1))
    tags_tag = soup.find('a', class_='rubric-header__link _active')
    tags = ''
    if tags_tag is not None:
        tags = tags_tag.get_text()
    result = {
        'title': title,
        'date': date_pub.strftime('%d.%m.%Y'),
        'content': content,
        'num_views': num_comments * 5,
        'num_comments': num_comments,
        'tags': tags
    }
    with open('news_lentaru.csv', 'a', encoding='utf-8') as file:
        keys = result.keys()
        writer = DictWriter(file, keys)
        writer.writeheader()
        writer.writerow(result)


def get_articles_by_day(date_look):
    base_link = form_link_from_date(date_look)
    page_num = 1
    continue_scrap = True
    while continue_scrap is True:
        link = f'{base_link}/page/{page_num}'
        driver.get(link)
        lxml = driver.page_source
        soup = BeautifulSoup(lxml, 'lxml')
        lis = soup.findAll('li', class_='archive-page__item _news')
        if len(lis) == 0:
            continue_scrap = False
        else:
            for li in lis:
                link = f"{root}{li.find('a')['href']}"
                get_article(link)
        page_num += 1


def get_news(date_from: date, date_to: date):
    dt_range = DatetimeRange(date_from, date_to)
    date_now = date_from
    articles = []
    print('processing...')
    while date_now in dt_range:
        get_articles_by_day(date_now)
        date_now += timedelta(days=1)
    driver.quit()

def write_news(path, news):
    keys = news[0].keys()
    with open(path, 'w', encoding='utf-8') as file:
        writer = DictWriter(file, keys)
        writer.writeheader()
        writer.writerows(news)

if __name__ == '__main__':
    start = date(2022, 10, 7)
    end = date.today()
    get_news(start, start)
    try:
        driver.quit()
    except:
        pass
    