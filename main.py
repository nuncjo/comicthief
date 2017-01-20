# -*- coding:utf-8 -*-

from concurrent.futures import ThreadPoolExecutor, wait
from collections import namedtuple
from pathlib import Path
import os
from urllib.parse import urlparse
from zipfile import ZipFile

import requests
from lxml import html

from config import get_config, CONFIG, HTML_TEMPLATE


def name_fits(search_phrase, key):
    if key:
        return search_phrase.lower() in key.lower()


class Base:

    def __init__(self):
        self.config = get_config(CONFIG)
        self.img_dir = self.config['SETTINGS'].get('img_dir', 'img')


class Fetcher(Base):

    def fetch_comic_list_page(self, service='default'):
        return requests.get(self.config['COMICS_LIST'].get(service))

    def fetch_subpage(self, url):
        return requests.get(url)

    def prepare_ordered_filename(self, remote_path, order):
        file_name = os.path.split(remote_path)[-1]
        return "{}.{}".format(str(order), file_name.split('.')[1])

    def download_image(self, url, local_path, name):
        download_path = Path(
            local_path,
            name
        )
        with download_path.open('wb') as f:
            f.write(requests.get(url).content)
            return download_path

    def download_images_list(self, local_path, images_list, threads=2):
        # TODO: dekorator with threadpol oraz timeit lub uzyc async, w koncu to python 3.6
        local_path.mkdir(parents=True, exist_ok=True)
        local_path_str = str(local_path)
        pool = ThreadPoolExecutor(threads)
        futures = []
        for order, image_url in enumerate(images_list):
            remote_path = urlparse(image_url).path
            file_name = self.prepare_ordered_filename(remote_path, order)
            futures.append(pool.submit(self.download_image, image_url, local_path_str, file_name))
        wait(futures)


class Extractor(Base):

    def extract_comic_links(self, page, service='default'):
        tree = html.fromstring(page.content)
        return tree.xpath(self.config['COMICS_LIST_XPATH'].get(service))

    def extract_issues_list(self, page, service='default'):
        tree = html.fromstring(page.content)
        x = tree.xpath(self.config['COMICS_SUBPAGE_XPATH'].get(service))
        return x

    def extract_images_list(self, page, service='default'):
        tree = html.fromstring(page.content)
        return tree.xpath(self.config['COMICS_IMAGES_XPATH'].get(service))


class Creator(Base):

    def create(self):
        raise NotImplementedError

    def make_comics_dict(self, hrefs):
        return {item.text: item.attrib.get('href') for item in hrefs}

    def search_comics_dict(self, search_phrase, comics_dict):
        return {key: value for key, value in comics_dict.items() if name_fits(search_phrase, key)}

    def exact_search_comics_dict(self, search_phrase, comics_dict):
        return {key: value for key, value in comics_dict.items() if search_phrase == key}


class CreatorCbz(Creator):

    def zip_directory(self, path, img_dir, name):
        with ZipFile(str(Path(path, "{}.cbz".format(name))), 'w') as zip_file:
            for file in os.listdir(str(Path(path, img_dir))):
                zip_file.write(Path(path, img_dir, file))

    def create(self, path, img_dir, name):
        self.zip_directory(path, img_dir, name)


class ComicThief:

    def __init__(self, root_path=None):
        self.fetcher = Fetcher()
        self.extractor = Extractor()
        self.creator = CreatorCbz()
        self.config = get_config(CONFIG)
        self.img_dir = self.config['SETTINGS'].get('img_dir', 'img')
        self.output_dir = self.config['SETTINGS'].get('output_dir', 'comics')
        self.cwd = root_path or Path.cwd()

    def fetch_comics_dict(self):
        page = self.fetcher.fetch_comic_list_page()
        return self.creator.make_comics_dict(self.extractor.extract_comic_links(page))

    def get_first_result(self, results):
        return sorted(results.items())[0][1]

    def find_results(self, keyword, exact=False):
        Results = namedtuple('Results', 'results_dict results_len')
        comics_dict = self.fetch_comics_dict()
        if exact:
            results = self.creator.exact_search_comics_dict(keyword, comics_dict)
        else:
            results = self.creator.search_comics_dict(keyword, comics_dict)
        return Results(results, len(results))

    def search(self, keyword):
        found = self.find_results(keyword)
        if found.results_len == 1:
            subpage = self.fetcher.fetch_subpage(self.get_first_result(found.results_dict))
            episodes = self.creator.make_comics_dict(self.extractor.extract_issues_list(subpage))
            print('\n'.join(episodes.keys()))
            return episodes
        elif found.results_len > 1:
            print('Found more than one result. Choose one of the results and use -xs <name>')
            print(found.results_dict)
            return found.results_dict
        else:
            print('Found nothing.')

    def exact_search(self, keyword):
        found = self.find_results(keyword, exact=True)
        if found.results_len == 1:
            print('You should specify one of the episodes.')
            subpage = self.fetcher.fetch_subpage(self.get_first_result(found.results_dict))
            episodes = self.creator.make_comics_dict(self.extractor.extract_issues_list(subpage))
            print('\n'.join(episodes.keys()))
            return episodes
        else:
            print('Found nothing.')

    def download_episode(self, episode_url, name):
        subpage = self.fetcher.fetch_subpage(episode_url + '/full')
        images_list = self.extractor.extract_images_list(subpage)
        self.fetcher.download_images_list(Path(self.cwd, self.output_dir, name, self.img_dir), images_list)
        self.creator.create(str(Path(self.cwd, self.output_dir, name)), self.img_dir, name)
        print('Episode downloaded.')

#ct = ComicThief()
#result = ct.search('Lobo')
