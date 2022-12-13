import json
import time
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib 
import datetime
import pandas as pd
matplotlib.use('Agg')

from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from . import predict_models, debug, views, admin


with open("predict\creds\credentials.json", "r") as f:
    creds = json.load(f)

def extract_html(html, market):
    soup = BeautifulSoup(html, 'html.parser')
    dates = list()
    values = list()

    for col in soup.find_all("tbody", attrs={"class": "b-history__table-body"}):
        for row in col:
            period = row.find("td").text
            values_list = row.find(class_='b-history__value-td').find_all(class_='b-history__number-part')
            value = int("".join([val.text for val in values_list]))
            
            dates.append(period)
            values.append(value)

    d = {'Период': dates, 'Значение': values}
    df = pd.DataFrame(data=d)
    df['Период'] = df['Период']
    df['Период'] = pd.to_datetime(df['Период'], dayfirst=True)
    df['Месяц'] = df['Период'].apply(lambda x: x.strftime("%B"))
    return df


def extract_ozon(driver, query, new_df):
    try:
        driver.get("https://seller.ozon.ru/app/registration/signin")

        for i in creds.get("ozon"):
            driver.delete_cookie(i)
            driver.add_cookie({"name": i, "value": creds.get("ozon").get(i)})

        driver.get("https://seller.ozon.ru/app/analytics/what-to-sell/all-queries")
        driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/div/div/a[6]")
        driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[1]").send_keys(query)
        content = driver.page_source

        df = extract_html(content, 'ozon')
        predicted_df = predict_models.predict_ozon(df)
        fig = sns.barplot(data=predicted_df, x="Месяц", y="Значение").set_title("Ozon")
        print(f"Ozon Successfully")
        fig.figure.savefig("static/img/ozon.png")
        plt.close()
    except:
        pass

def extract_wb(driver, query, new_df):
    try:
        driver.get("https://seller.wildberries.ru/popular-search-requests")

        for i in creds.get("wildberries"):
            driver.delete_cookie(i)
            driver.add_cookie({"name": i, "value": creds.get("wildberries").get(i)})

        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div/a[4]")
        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/label").send_keys(query)
        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/button[3]").click()
        time.sleep(5)
        content = driver.page_source

        df = extract_html(content, 'wb')
        predicted_df = predict_models.predict_wb(df)
        fig = sns.barplot(data=predicted_df, x="Месяц", y="Значение").set_title("Wildberries")
        print(f"WB Successfully")
        fig.figure.savefig("static/img/wildberries.png")
        plt.close()
    except:
        pass

def extract_avito(driver, query, new_df):
    try:
        driver.get("https://www.avito.ru/analytics/wordstat")

        for i in creds.get("avito"):
            driver.delete_cookie(i)
            driver.add_cookie({"name": i, "value": creds.get("avito").get(i)})

        driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/div/div/div[2]/a[2]")
        driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[4]").send_keys(query)
        driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div[1]").click()
        time.sleep(5)
        content = driver.page_source

        df = extract_html(content, 'avito')
        predicted_df = predict_models.predict_avito(df)
        fig = sns.barplot(data=predicted_df, x="Месяц", y="Значение").set_title("Avito")
        print(f"Avito Successfully")
        fig.figure.savefig("static/img/avito.png")
        plt.close()
    except:
        pass

def extract_wordstat(driver, query):
    df = views.lookup(driver, query, True)

    predicted_dict = predict_models.predict_yandex(df)
    predicted_df = pd.DataFrame(predicted_dict)
   

    fig = sns.barplot(data=final_df, x="Месяц", y="Значение").set_title("Яндекс")
    fig.figure.savefig(f"static/img/yandex_plot.png")
    plt.close()

    return df
