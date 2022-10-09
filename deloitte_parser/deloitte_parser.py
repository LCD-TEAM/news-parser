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

base_url = 'https://www2.deloitte.com'
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

def get_date_from_str(date_str):
    parts = date_str.split(' ')
    month = months[parts[1]]
    year = int(parts[2])
    day = int(parts[0])
    return date(year, month, day)

def get_links(url, num_articles):
    driver.get(url)
    num_links = 0
    links = []
    try:
        while num_links < num_articles:
            xpath = '/html/body/div[2]/div[1]/div/div[6]/div/div/div/div/div/div[3]/button[1]'
            elem = driver.find_element(by=By.XPATH, value=xpath)
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            driver.execute_script("return arguments[0].style.display='block';", elem)
            driver.execute_script("return arguments[0].scrollIntoView(true);", elem)
            if elem.is_displayed() is False:
                print('break')
                break
            webdriver.ActionChains(driver).click(elem).perform()
            num_links += 8
        html = driver.page_source
        html = BeautifulSoup(html, "lxml")
        articles = html.find_all('div', class_='blogpromo cmp-promo--featured-basic section display-block')
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
        final = pd.DataFrame({'links' : links})
        final = final[~final['links'].str.contains('#ws')]
        final = final.drop_duplicates(subset=['links'])
        return final

    except Exception as e:
        print(e)
        print('test')
        driver.quit()
        return None

def get_article(url):
    
    print(base_url + url)
    driver.get(base_url + url)
    plain_text = driver.page_source
    html = BeautifulSoup(plain_text, 'lxml')
    title = html.find('h1').get_text()
    date = get_date_from_str(html.find('span', class_='cmp-component-header__publish-date').get_text()).strftime('%d.%m.%Y')
    print(date)
    contents = []
    contents.append(html.find('h2').get_text())
    for div in html.findAll('div', class_='cmp-text'):
        children = div.findChildren('p', class_='')
        if children is not None:
            contents.append('\n'.join(list(map(lambda t: t.get_text(), children))))
    content = '\n'.join(contents)
    num_views = 0
    num_comments = 0
    tags_lst = html.find('ul', class_='cmp-tag-list').findChildren('li')
    tags = ';'.join(list(map(lambda t: t.get_text(), tags_lst)))
    result = {
        'title': title,
        'date': date,
        'content': content,
        'num_views': num_views,
        'num_comments': num_comments,
        'tags': tags
    }
    with open('deloitte_news.csv', 'a', encoding='utf-8') as file:
        keys = result.keys()
        writer = DictWriter(file, keys)
        writer.writerow(result)
    

def get_news(url, num_articles):
    print('parsing links')
    links = list(get_links(base_url + url, num_articles)['links'])
    news = []
    print('parsing articles')
    for link in links:
        get_article(link)
    driver.quit()

if __name__ == '__main__':
    url = '/global/en/insights/economy.html'
    num_articles = 40
    get_news(url, num_articles)