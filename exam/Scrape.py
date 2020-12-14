from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from multiprocessing.pool import ThreadPool
from threading import Thread
from queue import Queue
import multiprocessing
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import bs4
from time import sleep
import datetime
import matplotlib.pyplot as plt
import numpy as np
import re
import requests
import time
import csv
import pandas as pd
from random import randint
import pymongo
import pandas as pd

BASE_SEARCH_URL = 'https://bilhandel.dk/alle-biler/side-'
db = client.python_exam
collection = db.cars


def get_details_link(page_number):
    random = randint(5, 60)

    print(f'Getting detail links.. Waiting {random} seconds...')
    time.sleep(random)

    res = requests.get(BASE_SEARCH_URL + str(page_number))
    soup = bs4.BeautifulSoup(res.text, 'html.parser')

    browserSpans = soup.find_all('span', {'id': re.compile('car-headline*')})

    anchors = [span.find_parent('a') for span in browserSpans]
    urls = [a['href'] for a in anchors]

    print(f'Page number {page_number} scraped successfully')

    return urls


def download_car_details(car_url):
    random = randint(5, 60)
    time.sleep(random)
    headers = {'whoami': 'Vi beklager hvis vi er til besvær. Vi skal bruge data til eksamensprojekt i Python. Vi kan kontaktes på cph-mb346@cphbusiness.dk'}
    url = 'https://bilhandel.dk' + car_url
    res = requests.get(url, headers)
    if res.ok:
        return scrape_details(res, car_url)
    else:
        return {}


def scrape_details(car_details, url):
    soup = bs4.BeautifulSoup(car_details.text, 'html.parser')
    res = {}
    try:
        car_model = soup.find('h1').text.strip()
    except AttributeError:
        car_model = None

    try:
        car_price = soup.find('div', {'class': 'price'}
                              ).text.strip()
    except AttributeError:
        car_model = None

    try:
        spec_container = soup.find('div', {'class': 'spec-container'})
        spec_divs = spec_container.findAll('div', {'class': 'col-xs-4'})
    except AttributeError:
        return res

    for sd in spec_divs:
        try:
            label = sd.find('span', {'class': 'spec-label'}
                            ).text.strip().replace(':', '').replace('.', '')
            value = sd.find('span',
                            {'class': 'spec-value'}).text
            res[label] = value
        except AttributeError:
            continue

    res['Model'] = str(car_model)
    res['Pris'] = str(car_price)
    res['Link'] = str(url)
    print(f'{car_model} scraped successfully')
    return res


def multithreading(func, args, workers=3):
    with ThreadPoolExecutor(workers) as ex:
        res = ex.map(func, args)
    return list(res)


def multiprocess(func, args, workers=multiprocessing.cpu_count()):
    with ProcessPoolExecutor(workers) as ex:
        res = ex.map(func, args)
    return list(res)


def write_to_csv(filename, data):
    keys = [i for s in [d.keys() for d in data] for i in s]
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def clean_data(data):
    for car in data:
        if car is not None:
            for k, v in car.items():
                if k != 'Model':
                    car[k] = v.split(' ', 1)[0]
    return data


def read_urls():
    with open('data/urls.txt') as f:
        lines = f.read().splitlines()
        return lines


def writeUrlsToFile(urls):
    with open('data/urls.txt', 'w') as f:
        for url in urls:
            f.write("%s\n" % url)


def write_to_db(data):
    collection.insert_many(data)


def read_from_db():
    # Make a query to the specific DB and Collection
    cursor = collection.find({})

    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))

    print(df.head(2))


def go(page_count):
    df = pd.read_csv('data/bilhandel_unclean.csv')
    for column in df:
        if column is not 'Model':
            print(column)
            column = column.split(' ', 1)[0]
    print(df.head())
    # res = multithreading(get_details_link, [n for n in range(page_count)], 50)
    # urls = [y for x in res for y in x]
    #urls = read_urls()
    # writeUrlsToFile(urls)
    #cars_data = multithreading(download_car_details, urls, 100)
    #df = pd.DataFrame.from_dict(cars_data)
    #df.to_csv('data/bilhandel_unclean.csv', na_rep='-')
    #cars_data = clean_data(cars_data)

    # write_to_db(cars_data)
    #write_to_csv('data/bilhandel.csv', cars_data)
    # read_from_db()


if __name__ == "__main__":
    go(1)
