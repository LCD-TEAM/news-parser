from os.path import dirname, realpath, join
from datetime import date, timedelta
from bs4 import BeautifulSoup
import requests
import csv
import toml


PROJECT_DIR = join(dirname(realpath(__file__)), "..")
CONFIG_PATH = join(PROJECT_DIR, "config.toml")
config = toml.load(CONFIG_PATH)


def get_soup_news_date(year: int, month: int, day: int):
    """
    Возвращает soup страницы с новостями,
    выпущенные year.month.day
    """
    url = f'http://banki.ru/news/lenta/?filterType=all&d={day}&m={month}&y={year}'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    code_html = 'lf4cbd87d ld6d46e58 lb47af913'
    st = soup.find_all('div', class_=code_html)
    return st


def content_news(url: str):
    """
    Возвращает текст новости на странице url
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    code_html = 'l6d291019'
    st = soup.find_all('div', class_=code_html)[0]

    content = ""
    for p in st.find_all('p'):
        content += p.get_text()

    return content

def get_news(start: date, end: date):
    """
    Возвращает list новостей в промежутке времени
    от start до end
    """
    news = list()

    dates = [str(start + timedelta(days = x)) for x in range((end - start).days + 1)]

    for day_news in dates:
        for i in get_soup_news_date(*day_news.split('-')):
            if i.a is not None:
                date = i.find_all('div', class_='l31caf777')[0].get_text().strip()
                views_comments = i.find_all('span', class_='l1800f3ef')
                views = views_comments[0].get_text().strip()

                if len(views_comments) > 1:
                    comments = views_comments[1].get_text().strip()
                else:
                    comments = 0

                news.append({
                    'title': i.a.get_text().strip(),
                    'url': f"https://www.banki.ru{i.a['href']}",
                    'date': date,
                    'content': content_news(f"https://www.banki.ru{i.a['href']}"),
                    'num_views': views,
                    'num_comments': comments,
                })
    
    return news

def write_news(file_path: str, news: list):
    """
    Записывает news в file_path в формате csv
    """
    keys = news[0].keys()

    with open(file_path, 'w') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(news)

if __name__ == "__main__":
    # пример
    start = date(2022,10,1)
    end = date(2022,10,7)
    write_news(PROJECT_DIR + config['banki_ru_path'], get_news(start, end))