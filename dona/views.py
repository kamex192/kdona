from django.http import HttpResponse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


def get_fx_rate():
    options = Options()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.execute_script(
        'const newProto = navigator.__proto__;delete newProto.webdriver;navigator.__proto__ = newProto;')
    driver.get('https://crocro.com/tools/item/view_browser_inf.html')
    time.sleep(10)
    purchaseBox = driver.find_element_by_xpath(
        '//*[@id="purchaseBox"]/div/div/div[2]/form/button')
    time.sleep(3)
    purchaseBox.click()
    time.sleep(10)
    driver.quit()
    return 'usd_jpy'


def index(request):
    fx_rate = get_fx_rate()
    return HttpResponse(fx_rate)


def check(request):
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.google.com')
    # time.sleep(1)
    element = driver.find_element(By.CSS_SELECTOR, '[name="q"]')
    element.send_keys("ブラウザ情報 表示")
    # time.sleep(1)
    element.send_keys(Keys.ENTER)
    # time.sleep(1)
    selector = 'a'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        if 'ブラウザ情報表示' in element.text:
            url = element.get_attribute('href')
            print(url)
            element.send_keys(Keys.ENTER)
            break

    time.sleep(10)

    ret = '自動操縦フラグチェック：'

    selector = 'div.infArea'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        if 'window.navigator.webdriver' in element.text:
            if 'true' in element.text:
                ret = ret + 'ばれてるよー ' + element.text
                print(ret)

    return HttpResponse(ret)
