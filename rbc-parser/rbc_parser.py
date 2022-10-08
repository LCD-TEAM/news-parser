import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import re
import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import traceback
from datetime import datetime, date
from csv import DictWriter

def get_links(url):
    scroll_pause_time = 0.1
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    links = []

    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            print("break")
            break
        last_height = new_height
        html = driver.page_source
        html = BeautifulSoup(html, "lxml")
        articles = html.find_all('div', class_='item__wrap')
        previous_list = ''
        for article in articles:
            ankor_list = article.findChildren('a', class_='item__link')
            if ankor_list != previous_list:
                previous_url = ''
                for ankor in ankor_list:
                    url = ankor.get('href')
                    if url != previous_url:
                        links.append(url)
                    previous_url = url
            previous_list = ankor_list
    driver.quit()
    final = pd.DataFrame({'links' : links})
    final = final[~final['links'].str.contains('#ws')]
    final = final.drop_duplicates(subset=['links'])

    return final



def get_article(session, url):

    try:
        req = session.get(url)
        plain_text = req.text
        html = BeautifulSoup(plain_text, "lxml")
        title = html.find('h1', class_='article__header__title-in')
        title_final = title.get_text().lstrip().rstrip()
        date_pub = datetime.strptime(html.find('time', class_='article__header__date')['datetime'].split('T', 1)[0],"%Y-%m-%d").date().strftime('%d.%m.%Y')
        articles = html.find('div', {'class': 'article__text article__text_free'}).findChildren('p')
        article_text = '\n'.join(list(map(lambda t: t.get_text().lstrip().rstrip(), articles)))
        tags_container = html.findAll('a', class_='article__tags__item')
        tags = ';'.join(list(map(lambda t: t.get_text(), tags_container)))
        result = {
            'title' : title_final,
            'date': date_pub,
            'content' : article_text,
            'num_views': 0,
            'num_comments': 0,
            'tags': tags
            }
        with open('news_rbc.csv', 'a', encoding='utf-8') as file:
            keys = result.keys()
            writer = DictWriter(file, keys)
            writer.writerow(result)

    except Exception as e:
        print(url)
        title_final = ''
        article_text = ''



def get_news(url):
    links = list(get_links(url)['links'])
    news = []
    session = requests.Session()
    for link in links:
        get_article(session, link)


if __name__ == '__main__':
    url1 = 'https://www.rbc.ru/economics/?utm_source=topline'
    url2 = 'https://www.rbc.ru/business/?utm_source=topline'
    try:
        get_news(url1)
        get_news(url2)

    except Exception as e:
        
        print(e)
        print(traceback.format_exc())