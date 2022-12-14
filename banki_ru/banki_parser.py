from os.path import dirname, realpath, join
from datetime import date, timedelta
from bs4 import BeautifulSoup
import requests
import csv
import os
from selenium import webdriver

options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)
driver.quit()

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

    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    code_html = 'l6d291019'
    st = soup.find('div', class_=code_html)

    content = ""
    if st is not None:
        for p in st.find_all('p', recursive=False):
            content += p.get_text().strip()

    return content.strip()

def get_news(start: date, end: date, file_path: str):
    """
    Парсит страницы и записывает в file_path новости
    """
    
    dates = [str(start + timedelta(days = x)) for x in range((end - start).days + 1)][::-1]

    keys = ['title', 'url', 'date', 'content', 'num_views', 'num_comments']

    f = open(file_path, 'a')
    dict_writer = csv.DictWriter(f, keys)

    # если файл пуст, создаем новый csv и записываем туда keys
    # иначе просто дописываем в файл 
    if os.stat(file_path).st_size == 0:
        dict_writer.writeheader()

    for day_news in dates:
        with open(dirname(realpath(__file__)) + '/end_date.txt', 'w') as f_date:
            f_date.write(day_news)
        for i in get_soup_news_date(*day_news.split('-')):
            if i.a is not None:
                date = i.find_all('div', class_='l31caf777')[0].get_text().strip()
                views_comments = i.find_all('span', class_='l1800f3ef')
                views = views_comments[0].get_text().strip()
                url = f"https://www.banki.ru{i.a['href']}"
                content = content_news(url)

                if not content:
                    continue

                if len(views_comments) > 1:
                    comments = views_comments[1].get_text().strip()
                else:
                    comments = 0

                news = {
                    'title': i.a.get_text().strip(),
                    'url': url,
                    'date': date,
                    'content': content,
                    'num_views': views,
                    'num_comments': comments,
                }

                dict_writer.writerow(news)
    

if __name__ == "__main__":
    # пример
    start = date(2022,3,18)

    # раскомментить, если начальную дату берешь из файла

    # with open(dirname(realpath(__file__)) + '/end_date.txt', 'r') as f_date:
    #     start = date(*list(map(int, f_date.readline().split('-'))))

    end = date(2022,8,17)
    #get_news(start, end, PROJECT_DIR + config['banki_ru_path'])