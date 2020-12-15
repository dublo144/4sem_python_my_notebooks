from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from multiprocessing.pool import ThreadPool
from threading import Thread
import multiprocessing
import bs4
from time import sleep
import requests
import time
import csv
import pandas as pd
from random import randint
import pandas as pd
import re
import pymongo

client = pymongo.MongoClient()
db = client.python_exam
collection = db.cars


class car_scraper():
    def __init__(self, pages_to_scrape, output_file):
        self.BASE_SEARCH_URL = 'https://bilhandel.dk/alle-biler/side-'
        self.output_file = output_file
        self.pages_to_scrape = pages_to_scrape
        self.car_urls = []
        self.scraped_cars = []

    def __iter__(self):
        return self

    def get_detail_links(self, page_number):
        random = randint(5, 10)

        print(f'Getting detail links.. Waiting {random} seconds...')
        time.sleep(random)

        res = requests.get(self.BASE_SEARCH_URL + str(page_number))
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        browserSpans = soup.find_all(
            'span', {'id': re.compile('car-headline*')})

        anchors = [span.find_parent('a') for span in browserSpans]
        urls = [a['href'] for a in anchors]

        print(f'Page number {page_number} scraped successfully')

        return urls

    def scrape_car_details(self, car_details, url):
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

    def download_car_details(self, car_url):
        random = randint(5, 10)
        time.sleep(random)
        headers = {'whoami': 'Vi beklager hvis vi er til besvær. Vi skal bruge data til eksamensprojekt i Python. Vi kan kontaktes på cph-mb346@cphbusiness.dk'}
        url = 'https://bilhandel.dk' + car_url
        res = requests.get(url, headers)
        if res.ok:
            return self.scrape_car_details(res, car_url)
        else:
            return {}

    def save_to_csv(self, dataframe):
        dataframe.to_csv(self.output_file)

    def clean_data(self, df):
        df = df.apply(lambda x: x.str.replace(
            '-', '') if x.name != 'Model' else x)
        df = df.apply(lambda x: x.str.replace(
            '.', '') if x.name != 'Model' else x)
        df = df.apply(lambda x: x.str.split(' ', n=1).str[
            0] if x.name != 'Model' else x)
        df[['Make', 'Model']] = df['Model'].str.split(' ', 1, expand=True)
        return df

    def save_to_db(self, df):
        collection.insert_many(df)

    def scrape(self, threads=3):
        with ThreadPoolExecutor(threads) as ex:
            res = ex.map(self.get_detail_links, [
                n for n in range(self.pages_to_scrape)])
            self.car_urls = list(res)

        with ThreadPoolExecutor(threads) as ex:
            res = ex.map(self.download_car_details, [
                y for x in self.car_urls for y in x])
            self.scraped_cars = list(res)

        df = pd.DataFrame.from_dict(self.scraped_cars)

        clean_df = self.clean_data(df)

        self.save_to_csv(clean_df)


if __name__ == '__main__':
    scraper = car_scraper(1, 'data/bilhandel_clean.csv')
    # scraper.scrape(20)
    df = pd.read_csv('data/bilhandel_unclean.csv')
    df = df.applymap(str)
    df = scraper.clean_data(df)
    scraper.save_to_csv(df)
    scraper.save_to_db(df.to_dict('records'))
