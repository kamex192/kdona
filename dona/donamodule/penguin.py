from . import common
from dona.models import Penguin

import chromedriver_binary

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import threading
import time

import re
import random


class GetPenguinThread(threading.Thread):
    def run(self):
        print('GetPenguinThread start')
        print('active_count:' + str(threading.active_count()))
        print('enumerate:' + str(threading.enumerate()))

        # ドライバ初期化
        driver = common.init_driver()

        # googleでサイト検索
        # site = 'Sidejob-Hack | 副業'
        # common.move_toppage_from_google(driver, site)
        driver.get('https://fukugyo-freelife.com/')
        base_url = driver.current_url
        print(base_url)

        # アイテム検索
        rand_page_list = get_rand_page_list(driver)

        print('start roop base base_url')
        print(base_url)
        for page in rand_page_list:
            print('page:' + str(page))
            url_page = base_url + 'page/' + str(page+1)
            print(url_page)
            print('base url')
            print(base_url)
            urls = fetch_article_urls(driver, url_page)
            for url in urls:
                print('urls roop')
                print(url)
                driver.get(url)
                parse_article(driver)

        print('GetPenguinThread end')


def get_rand_page_list(driver):
    print('get_rand_page_list start')

    max_page = 0

    wait = WebDriverWait(driver, 30)
    selector = 'div.pagination span.dots + a'
    element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, selector)))
    url = element.get_attribute('href')
    print(url)
    pattern = '.*?page.(\d+)'
    result = re.match(pattern, url)
    if result is not None:
        print(result)
        max_page = result.group(1)
        print(max_page)

    page_list = list(range(int(max_page)))
    rand_page_list = random.sample(page_list, len(page_list))
    print(rand_page_list)

    print('get_rand_page_list end')
    return rand_page_list


def fetch_article_urls(driver, url):
    print('fetch_article_urls start')
    print(url)
    url_list = []

    driver.get(url)
    wait = WebDriverWait(driver, 30)
    selector = 'main a'
    elements = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, selector)))
    for element in elements:
        if '】' in element.text:
            print(element.text)
            url = element.get_attribute('href')
            print(url)
            url_list.append(url)

    print('fetch_article_urls end')
    return url_list


def parse_article(driver):
    print('parse_article start')

    penguin = Penguin()
    penguin.url = driver.current_url
    print(penguin.url)

    wait = WebDriverWait(driver, 30)
    selector = 'h1.entry-title'
    element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, selector)))

    penguin.name = element.text
    print(element.text)

    selector = 'time.entry-date'
    element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, selector)))

    penguin.post_date = element.text
    print(element.text)

    try:
        selector = 'p'
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, selector)))
        for element in elements:
            if '定価：' in element.text:
                print(element.text)
                print(re.sub("[^0-9]+", "", element.text))
                penguin.list_price = re.sub("[^0-9]+", "", element.text)
            if '販売開始：' in element.text:
                print(element.text)
            if '受注締切：' in element.text:
                print(element.text)
            if '発売：' in element.text:
                print(element.text)

    except Exception as e:
        print(e)

    selector = 'article'
    element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, selector)))
    penguin.recommended_word = parse_recommended_word(element.text)
    print('recommended_word')
    print(penguin.recommended_word)

    try:
        print(vars(penguin))
        penguin.save()
        print('penguin.save')
        time.sleep(3)
    except Exception as e:
        print(e)

    print('parse_article end')


def parse_recommended_word(word):
    print('parse_recommended_word start')

    recommended_word = ''
    if '人気' in word:
        recommended_word = '人気'
    if '前作' in word:
        recommended_word = '前作'
    if '注意' in word:
        recommended_word = '注意'
    if '完売' in word:
        recommended_word = '完売'
    if '復活' in word:
        recommended_word = '復活'
    if '1位' in word:
        recommended_word = '1位'
    if '即完' in word:
        recommended_word = '即完'
    if 'やばい' in word:
        recommended_word = 'やばい'
    if '大化け' in word:
        recommended_word = '大化け'
    if '寝かし' in word:
        recommended_word = '寝かし'
    if '限定' in word:
        recommended_word = '限定'
    if '初回限定' in word:
        recommended_word = '初回限定'
    if '超' in word:
        recommended_word = '超'
    if '再販' in word:
        recommended_word = '再販'
    if '抽選' in word:
        recommended_word = '抽選'
    if '受注' in word:
        recommended_word = '受注'
    if '様子見' in word:
        recommended_word = '様子見'
    if 'おススメ' in word:
        recommended_word = 'おススメ'
    if '購入しました' in word:
        recommended_word = '購入しました'

    print('parse_recommended_word end')
    return recommended_word


def output_csv():
    print('output_csv start')
    response = common.output_csv(
        'Penguin', Penguin._meta, Penguin.objects.all())
    print('output_csv end')
    return response
