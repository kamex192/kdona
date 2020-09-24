from . import common
from dona.models import Gei

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


class GetGeiThread(threading.Thread):
    def run(self):
        print('GetGeiThread start')
        print('active_count:' + str(threading.active_count()))
        print('enumerate:' + str(threading.enumerate()))

        # ドライバ初期化
        driver = common.init_driver()

        # googleでサイト検索
        site = '芸は身を助ける。 - livedoor Blog'
        common.move_toppage_from_google(driver, site)

        # アイテム検索
        rand_page_list = get_rand_page_list(driver)

        url = driver.current_url
        for page in rand_page_list:
            print('page:' + str(page))
            url_page = url + '?p=' + str(page+1)
            print(url_page)
            get_gei_info(driver, url_page)

        print('GetGeiThread end')


def get_gei_info(driver, url):
    print('get_gei_info start')
    print(url)

    driver.get(url)

    wait = WebDriverWait(driver, 30)
    selector = 'div.article-outer'
    elements = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, selector)))
    for element in elements:
        gei = Gei()
        selector = 'abbr.updated'
        post_date_element = element.find_element_by_css_selector(selector)
        gei.post_date = post_date_element.text.replace(
            '年', '-').replace('月', '-').replace('日', ' ')
        print(post_date_element.text)
        selector = 'div.article-title-outer'
        name_element = element.find_element_by_css_selector(selector)
        gei.name = name_element.text
        print(name_element.text)
        selector = 'h2 a'
        url_element = element.find_element_by_css_selector(selector)
        url = url_element.get_attribute('href')
        gei.url = url
        print(url)

        selector = 'div.article-body-inner'
        body_inner_element = element.find_element_by_css_selector(selector)
        print('body_inner_element')
        print(body_inner_element.text)
        pattern = '[\s\S]*￥(.*)'
        result = re.match(pattern, body_inner_element.text)
        if result is not None:
            gei.price = re.sub("[^0-9]+", "", result.group(1))
            print('inner price')
            print(gei.price)

        gei.recommended_word = parse_recommended_word(gei.name)
        print('recommended_word')
        print('gei.recommended_word')

        try:
            print(vars(gei))
            gei.save()
            print('gei.save')
            time.sleep(3)
        except Exception as e:
            print(e)

    print('get_gei_info end')


def parse_recommended_word(name):
    print('parse_recommended_word start')

    recommended_word = ''
    if '人気' in name:
        recommended_word = '人気'
    if '前作' in name:
        recommended_word = '前作'
    if '注意' in name:
        recommended_word = '注意'
    if '完売' in name:
        recommended_word = '完売'
    if '復活' in name:
        recommended_word = '復活'
    if '1位' in name:
        recommended_word = '1位'
    if '即完' in name:
        recommended_word = '即完'
    if 'やばい' in name:
        recommended_word = 'やばい'
    if '大化け' in name:
        recommended_word = '大化け'
    if '寝かし' in name:
        recommended_word = '寝かし'
    if '限定' in name:
        recommended_word = '限定'
    if '初回限定' in name:
        recommended_word = '初回限定'
    if '超' in name:
        recommended_word = '超'
    if '再販' in name:
        recommended_word = '再販'
    if '抽選' in name:
        recommended_word = '抽選'

    print('parse_recommended_word end')
    return recommended_word


def get_rand_page_list(driver):
    print('get_rand_page_list start')

    max_page = 0

    selector = 'li.paging-last a'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        url = element.get_attribute('href')
        print(url)
        pattern = '.*?p=(\d+)'
        result = re.match(pattern, url)
        if result is not None:
            print(result)
            max_page = result.group(1)
            print(max_page)
        break

    page_list = list(range(int(max_page)))
    rand_page_list = random.sample(page_list, len(page_list))
    print(rand_page_list)

    print('get_rand_page_list end')
    return rand_page_list


def output_csv():
    print('output_csv start')
    response = common.output_csv(
        'Gei', Gei._meta, Gei.objects.all())
    print('output_csv end')
    return response
