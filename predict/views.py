from django.shortcuts import render
from django.http import HttpResponse
from twocaptcha import TwoCaptcha
from bs4 import BeautifulSoup
from . import source

from pytrends.request import TrendReq
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import time
import requests as rq
import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib 
matplotlib.use('Agg')

def index(request):
    return render(request, 'index.html')

def clean_period(str):
    return str.split("-")[0]

def month_name(str):
    return str.strftime("%B")

def extract_data(html, query):
    soup = BeautifulSoup(html, 'html.parser')

    dates = list()
    values = list()

    for col in soup.find_all("tbody", attrs={"class": "b-history__table-body"}):
        for row in col:
            period = row.find("td").text
            # На яндексе части от значений разделены в разные span элементы
            values_list = row.find(class_='b-history__value-td').find_all(class_='b-history__number-part')
            value = int("".join([val.text for val in values_list]))
            
            dates.append(period)
            values.append(value)

    d = {'Период': dates, 'Значение': values}
    df = pd.DataFrame(data=d)
    df['Период'] = df['Период'].apply(clean_period)
    df['Период'] = pd.to_datetime(df['Период'], dayfirst=True)
    df['Месяц'] = df['Период'].apply(month_name)

    return df

def auth(driver):
    '''
    Функция производит авторизацию в Yandex Wordstat для переданного driver

    Arguments:
        driver (obj): Объект selenium с открытой страницей авторизации Yandex Wordstat
    Returns:
        None: функция мутирует существующий объект driver
    '''
    login = "alexshevnew2022@yandex.ru"
    password = "alexshev34"

    driver.find_element(By.XPATH, "/html/body/form/table/tbody/tr[2]/td[2]/div/div[2]/span/span/input").send_keys(login)
    driver.find_element(By.XPATH, "/html/body/form/table/tbody/tr[2]/td[2]/div/div[3]/span/span/input").send_keys(password)
    driver.find_element(By.XPATH, "/html/body/form/table/tbody/tr[2]/td[2]/div/div[5]/span[1]/input").click()

def captcha_processing(src):
    '''
    Функция выгружает капчу из Yandex Wordstat и отправляет её в сервис ruCAPTCHA
    Argument:
        src (string): ссылка на капчу
    Returns:
        result (string): возвращает текст разгаданной капчи
    '''
    API_KEY = "69aea7580fad254d2994a3f8ddfec60d"
    response = rq.get(src)
    # Сохранение капчи
    out = open("captcha/img.jpg", "wb")
    out.write(response.content)
    out.close()
    # Отправка запроса к rucaptcha
    solver = TwoCaptcha(API_KEY)
    result = solver.normal('captcha/img.jpg')

    return result.get("code")

def lookup(driver, query, query_type):
    driver.get(f"https://wordstat.yandex.ru/#!/history?words={query}")
    driver.implicitly_wait(15)
    print("Log: get query is done")
    # Авторизация Yandex Wordstat
    try:
        auth(driver)
        print("Log: Authorization is done")
    except:
        pass
    # Загрузка капчи и получение расшифровки
    try:
        captcha_src = driver.find_element(By.XPATH, "/html/body/div[7]/div/div/table/tbody/tr/td/div/form/table/tbody/tr[1]/td/img[1]").get_attribute("src")
        captcha_text = captcha_processing(captcha_src)
        time.sleep(1)
        print(f"Log: Captcha is {captcha_text}")
        # Введение расшифровки и отправка капчи
        driver.find_element(By.XPATH, "/html/body/div[7]/div/div/table/tbody/tr/td/div/form/table/tbody/tr[2]/td[1]/span/span/input").send_keys(captcha_text)
        driver.find_element(By.XPATH, "/html/body/div[7]/div/div/table/tbody/tr/td/div/form/table/tbody/tr[2]/td[2]/span/input").click()
        time.sleep(1)
    except:
        pass
    # Загрузка html-исходников для дальнейшего парсинга
    content = driver.page_source

    df = extract_data(content, query)
    return df

def predict(request):

    def driver_init():
        service = Service(executable_path=ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1920x935')

        driver = webdriver.Chrome(service=service, chrome_options=options)
        driver.wait = WebDriverWait(driver, 5)
        return driver

    query = request.GET.getlist('query', '')[0].replace("?track_id", "")
    query_type = request.GET.getlist('query_type', '')[0]
    service = request.GET.getlist('service', '')[0]

    if query_type == "1":
        query_name = f"Купить {query.lower()}"
        query_price = f"Цена {query.lower()}"
    elif len(query) == 0 and query_type == "0":
        if service == 'Ремонт, строительство':
            query_name = 'ремонт и строительство'
        elif service == 'Мастер на час':
            query_name = 'мастер на час'
        elif service == 'Сад, благоустройство':
            query_name = 'услуга сада'
        elif service == 'Транспорт, перевозки':
            query_name = 'услуга перевозок'
        elif service == 'Обучение, курсы':
            query_name = 'обучение курсов'
        elif service == 'Красота, здоровье':
            query_name = 'красота и здоровье'
        elif service == 'Ремонт и обслуживание техники':
            query_name = 'ремонт техники'
        elif service == 'Праздники, мероприятия':
            query_name = 'проведение мероприятий'
        elif service == 'Доставка еды и продуктов':
            query_name = 'доставка продуктов'
        elif service == 'IT, интернет':
            query_name = 'подключение интернет'
        elif service == 'Реклама':
            query_name = 'услуга рекламы'
        elif service == 'Охрана, безопасность':
            query_name = 'охранные системы'
        elif service == 'Бытовые услуги':
            query_name = 'бытовые услуги'
    else:
        query_name = query
    # Получение данных Яндекс
    driver = driver_init()
    new_df = source.extract_wordstat(driver, query_name)
    price_df = source.extract_wordstat(driver, query_price)
    driver.quit()

    new_df['Значение'] = new_df['Значение'] + price_df['Значение']

    if query_type == "1":
        source.extract_ozon("chromedriver", query_name, new_df)
        source.extract_wb("chromedriver", query_name, new_df)

        return render(request, 'predict.html', context={'yandex_plot_path': "img/yandex_plot.png", 'ozon_path': 'img/ozon.png', 'wildberries_path': 'img/wildberries.png'})
    else:
        source.extract_avito("firefox", query_name, new_df)

        if len(query_name) == 0:
            return render(request, 'predict_service.html', context={'avito_path': "img/avito.png"})
        else:
            return render(request, 'predict_service.html', context={'yandex_plot_path': "img/yandex_plot.png", 'avito_path': "img/avito.png"})
