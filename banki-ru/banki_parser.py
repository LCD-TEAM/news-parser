from bs4 import BeautifulSoup
import requests
import itertools
from datetime import date, timedelta
import csv

def get_soup_news_date(year: int, month: int, day: int):
    url = f"http://banki.ru/news/lenta/?filterType=all&d={day}&m={month}&y={year}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    code_html = "lf4cbd87d ld6d46e58 lb47af913"
    st = soup.find_all('div', class_=code_html)
    return st


def get_news(start: date, end: date):
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
                    'num_views': views,
                    'num_comments': comments,
                })
    
    return news

def write_news(file_path: str, news: list):
    keys = news[0].keys()

    with open(file_path, 'w') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(news)

if __name__ == "__main__":
    start = date(2022,10,1)
    end = date(2022,10,7)
    write_news("news_banki.csv", get_news(start, end))