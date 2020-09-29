from django.http import HttpResponse

import chromedriver_binary

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import datetime
import csv
import urllib


def init_driver():
    print('init_driver start')
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(
        f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36 Edg/79.0.309.65')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(100, 200)
    print('init_driver end')
    return driver


def move_toppage_from_google(driver, site):
    print('move_toppage start')
    driver.get('https://www.google.com')

    wait = WebDriverWait(driver, 30)
    selector = '[name="q"]'
    element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, selector)))

    element.send_keys(site)
    element.send_keys(Keys.ENTER)

    selector = 'a'
    elements = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, selector)))
    for element in elements:
        print(element.text)
        if site in element.text:
            url = element.get_attribute('href')
            print(url)
            element.send_keys(Keys.ENTER)
            break

    print('move_toppage end')


def output_csv(file_name, meta, data_list):
    print('output_csv start')

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

    response = HttpResponse(content_type='text/csv; charset=UTF-8')
    filename = urllib.parse.quote(
        (file_name + '_' + str(now.date()) + '.csv').encode("utf8"))
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(
        filename)
    writer = csv.writer(response)

    field_names = [field.name for field in meta.fields]
    print(meta.fields)
    writer.writerow(meta.fields)
    for data in data_list:
        writer.writerow([getattr(data, field) for field in field_names])
    print('output_csv end')

    return response
