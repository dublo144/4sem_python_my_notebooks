import requests
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import time
import matplotlib.pyplot as plt


class book_reader():
    def __init__(self, url_list):
        self.url_list = url_list
        self.filenames = []

    def __iter__(self):
        return self

    def __next__(self):
        """Return the next filename (stops when no more)"""
        raise NotImplementedError

    def download(self, url):
        """Downloads from the url, to the file specified. Throws NotFoundException if 404"""
        res = requests.get(url)
        bookId = url.split('/')[-2]
        filepath = f'data/{bookId}.txt'
        try:
            if res.ok:
                with open(filepath, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=1024):
                        f.write(chunk)
                    print(f'{bookId} downloaded to {filepath}...')
                    return filepath

            elif res.status_code == 404:
                raise FileNotFoundError
        except FileNotFoundError as error:
            print('Error: ' + repr(error))

    def multi_download(self):
        """Uses threads to download multiple urls as text and stores filenames as a property."""
        with ThreadPoolExecutor(5) as ex:
            res = ex.map(self.download, self.url_list)
            self.filenames = list(res)

    def urllist_generator(self):
        """Returns a generator to loop through the urls"""
        for url in self.url_list:
            yield (url)

    def avg_vowels(self, text):
        """Rough estimate on readability - avg number of vowels in the words of the text"""
        with open(text, 'r') as f:
            data = f.read()
            number_of_words = len(data.split())
            number_of_vowels = sum(c.lower() in 'aeiou' for c in data)
        return (text, number_of_vowels / number_of_words)

    def calc_readability(self):
        """Calculates readablility and returns a sorted list of tuples of (bookid, avg_vowels)"""
        with ProcessPoolExecutor(multiprocessing.cpu_count()) as ex:
            results = list(ex.map(self.avg_vowels, self.filenames))
        return sorted(results, key=lambda x: x[1], reverse=True)

    def hardest_read(self):
        """Return the name of the file with the highest vowel score (using all cpu cores)"""
        avg_vowels = [self.avg_vowels(file) for file in self.filenames]
        return sorted(avg_vowels, key=lambda x: x[1], reverse=True)[0]

    def hardest_read_multiprocess(self):
        return self.calc_readability()[0]

    def plot_hardest_read(self):
        results = self.calc_readability()
        book_ids = list(zip(*results))[0]
        readability = list(zip(*results))[1]
        plt.barh(book_ids, readability)
        plt.grid(axis='x')
        plt.ylabel("Book IDs")
        plt.xlabel("Readablilty (Avg vowels pr. word)")
        plt.show()


if __name__ == "__main__":
    urls = ['https://www.gutenberg.org/files/1342/1342-0.txt',
            'https://www.gutenberg.org/files/11/11-0.txt',
            'http://www.gutenberg.org/cache/epub/1497/pg1497.txt',
            'https://www.gutenberg.org/files/25344/25344-0.txt',
            'https://www.gutenberg.org/files/1250/1250-0.txt',
            'https://www.gutenberg.org/files/1952/1952-0.txt',
            'http://www.gutenberg.org/cache/epub/1232/pg1232.txt',
            'https://www.gutenberg.org/files/84/84-0.txt',
            'https://www.gutenberg.org/files/98/98-0.txt',
            'http://www.gutenberg.org/cache/epub/2542/pg2542.txt'
            ]

    book_reader = book_reader(urls)
    book_reader.multi_download()

    start = time.perf_counter()
    print(book_reader.hardest_read())
    finish = time.perf_counter()
    print(f'Finished in {round(finish-start, 2)} seconds')

    start = time.perf_counter()
    print(book_reader.hardest_read_multiprocess())
    finish = time.perf_counter()
    print(f'Finished in {round(finish-start, 2)} seconds')

    book_reader.plot_hardest_read()
