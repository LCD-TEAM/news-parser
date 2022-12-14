from selenium import webdriver
import re
from bs4 import BeautifulSoup
from datetime import date, datetime
from csv import DictWriter

url = 'https://buh.ru'    

class DatetimeRange:
    def __init__(self, dt1, dt2):
        self._dt1 = dt1
        self._dt2 = dt2

    def __contains__(self, dt):
        return self._dt1 <= dt <= self._dt2

options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)
driver.quit()

def _get_num_views(html):
    res = re.search('\$\("\.data_post\s*\.views"\)\.text\(\s*(\d*)\)', html)
    if res is not None:
        return int(res.group(1))
    return 0

def _get_num_comments(soup):
    nc = soup.find('span', class_='comments_leave')
    if nc is not None:
        return int(nc.get_text())
    return 0

def _get_tags(soup):
    ls = soup.findAll('div', class_='rubric')
    themes = ';'.join(list(map(lambda t: ';'.join(t.get_text().rstrip().split(',')), ls[0].findAll('a'))))
    if len(ls) > 1:
        rubrics = ';'.join(list(map(lambda t: ';'.join(t.get_text().rstrip().split(', ')), ls[1].findAll('a'))))
    else:
        rubrics = ''
    return themes + ';' + rubrics

def get_news(date_from, date_to, file_path):
    dt_range = DatetimeRange(date_from, date_to)
    page_num = 1
    continue_scrap = True
    while continue_scrap is True:
        driver.get(f'https://buh.ru/news/uchet_nalogi/?PAGEN_1={page_num}')
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        news_headers = soup.findAll('article', class_='article')
        for news_header in news_headers:
            link = news_header.find('a')['href']
            driver.get(url + link)
            news_page = driver.page_source
            news_soup = BeautifulSoup(news_page, 'lxml')
            date_str = news_soup.find('span', class_='grayd').get_text()
            article = news_soup.find('div', class_='tip-news', itemprop='articleBody').findChildren('p')
            if datetime.strptime(date_str, '%d.%m.%Y').date() in dt_range:
                result = {
                    'title': news_soup.find('h1', class_='margin_line-height phead specdiv').get_text(),
                    'date': date_str,
                    'content': '\n'.join(list(map(lambda t: t.get_text().rstrip(), article))),
                    'num_views': _get_num_views(news_page),
                    'num_comments': _get_num_comments(news_soup),
                    'tags': _get_tags(news_soup)
                }
                path = file_path
                with open(path, 'a', encoding='utf-8') as file:
                    keys = result.keys()
                    writer = DictWriter(file, keys)
                    writer.writerow(result)
            else:
                continue_scrap = False
                break
        page_num += 1
    driver.quit()

def write_news(path, news):
    keys = news[0].keys()

    with open(path, 'w', encoding='utf-8') as file:
        writer = DictWriter(file, keys)
        writer.writeheader()
        writer.writerows(news)
    