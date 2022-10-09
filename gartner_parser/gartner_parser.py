import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import pandas as pd
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

months = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}

base_url = 'https://www.gartner.com'
url = '/smarterwithgartner/archive'

def get_date_from_str(date_str):
    parts = date_str.split(' ')
    month = months[parts[0]]
    year = int(parts[2])
    day = int(parts[1].replace(',', ''))
    return date(year, month, day)

def get_links(url, num_articles):
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    num_links = 0
    links = []
    try:
        while num_links < num_articles:
            xpath = '//*[@id="gartnerinternalpage-b3a76c580b"]/div[2]/div/div/div/div/div/div[2]/section/div/div[1]/div/div/section/div[4]/div[1]/a'
            elem = driver.find_element(by=By.XPATH, value=xpath)
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            driver.execute_script("return arguments[0].style.display='block';", elem)
            driver.execute_script("return arguments[0].scrollIntoView(true);", elem)
            if elem.is_displayed() is False:
                break
            webdriver.ActionChains(driver).click(elem).perform()
            num_links += 8
        html = driver.page_source
        html = BeautifulSoup(html, "lxml")
        articles = html.find_all('div', class_='individual-block list page-1')
        previous_list = ''
        for article in articles:
            ankor_list = article.findChildren('a')
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

    except Exception as e:
        return None
    finally:
        driver.quit()

def get_article(session, url, file_path):
    try:
        req = session.get(base_url + url)
        plain_text = req.text
        html = BeautifulSoup(plain_text, 'lxml')
        title = html.find('div', class_='hero-content').findChild('h1').get_text()
        date = get_date_from_str(html.find('span', class_='p-small').get_text()).strftime('%d.%m.%Y')
        contents = []
        contents.append(html.find('p', class_='p-intro-lg').get_text())
        for div in html.findAll('div', class_='cmp-globalsite-articletext'):
            children = div.findChildren('p', class_='')
            if children is not None:
                contents.append('\n'.join(list(map(lambda t: t.get_text(), children))))
        content = '\n'.join(contents)
        num_views = 0
        num_comments = 0
        tags = html.findAll('a', class_='hero-breadcrumb hero-breadcrumb-url')[1].get_text()
        result = {
            'title': title,
            'date': date,
            'content': content,
            'num_views': num_views,
            'num_comments': num_comments,
            'tags': tags
        }
        with open(file_path, 'a', encoding='utf-8') as file:
            keys = result.keys()
            writer = DictWriter(file, keys)
            writer.writerow(result)
    except Exception as e:
        pass

def get_news(num_articles, file_path):
    links = list(get_links(base_url + url, num_articles)['links'])
    news = []
    session = requests.Session()
    for link in links:
        get_article(session, link, file_path)
