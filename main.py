# -*- coding:utf-8 -*-

from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path
import os
from urllib.parse import urlparse

import requests
from lxml import html
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QImage, QPdfWriter, QPainter, QPagedPaintDevice

from .config import get_config, CONFIG, HTML_TEMPLATE

CWD = Path.cwd()


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
        img = requests.get(url)
        download_path = Path(
            Path.cwd(),
            local_path,
            self.img_dir,
            name
        )
        with download_path.open('wb') as f:
            f.write(img.content)
            return download_path

    def download_images_list(self, local_path, images_list, threads=2):
        # TODO: dekorator with threadpol oraz timeit
        pool = ThreadPoolExecutor(threads)
        futures = []
        for order, image_url in enumerate(images_list):
            remote_path = urlparse(image_url).path
            file_name = self.prepare_ordered_filename(remote_path, order)
            futures.append(pool.submit(self.download_image, image_url, local_path, file_name))
        wait(futures)


class Extractor(Base):

    def extract_comic_links(self, page, service='default'):
        tree = html.fromstring(page.content)
        return tree.xpath(self.config['COMICS_LIST_XPATH'].get(service))

    def extract_issues_list(self, page, service='default'):
        tree = html.fromstring(page.content)
        return tree.xpath(self.config['COMICS_SUBPAGE_XPATH'].get(service))

    def extract_images_list(self, page, service='default'):
        tree = html.fromstring(page.content)
        return tree.xpath(self.config['COMICS_IMAGES_XPATH'].get(service))


class Creator(Base):

    def make_comics_dict(self, hrefs):
        return {item.text: item.attrib.get('href') for item in hrefs}

    def search_comics_dict(self, search_phrase, comics_dict):
        return {key: value for key, value in comics_dict.items() if name_fits(search_phrase, key)}

    def make_comic_html(self, local_path):
        files = next(os.walk(str(Path(local_path, self.img_dir))))[2]
        images_html = ''.join(['<img src="{}"/>'.format(str(Path(CWD, local_path, self.img_dir, file)))
                               for file in sorted(files, key=lambda x: int(x.split('.')[0]))])
        return HTML_TEMPLATE.format(images_html)

    def make_comic_images_paths_list(self, local_path):
        files = next(os.walk(str(Path(local_path, self.img_dir))))[2]
        images_paths_list = [str(Path(CWD, local_path, self.img_dir, file))
                       for file in sorted(files, key=lambda x: int(x.split('.')[0]))]
        return images_paths_list

    def create_comic_html_file(self, local_path, name):
        with Path(Path.cwd(), local_path, name).open('w') as f:
            f.write(self.make_comic_html(local_path))

    def create_comic_pdf_file(self, local_path, name):
        with Path(Path.cwd()).joinpath(local_path, name).open('w') as f:
            f.write(self.make_comic_html(local_path))

    def make_pdf_from_images_list(self, path_list, local_path, name):
        image_coords = QPoint(0, 0)
        pdf_writer = QPdfWriter(str(Path(Path.cwd(), local_path, name)))
        pdf_writer.setPageSize(QPagedPaintDevice.A4)
        pdf_writer.setResolution(215)
        painter = QPainter(pdf_writer)

        for img_path in path_list:
            image = QImage(img_path)
            painter.drawImage(image_coords, image.scaledToWidth(1600))
            pdf_writer.newPage()

        pdf_writer.deleteLater()

    def make_cbr_from_images_list(self):
        #http://www.makeuseof.com/tag/create-cbrcbz-files-distribute-comic-strip-graphic/
        pass

    def compress_images(self):
        #TODO: to chyba cos dla rusta
        pass


class CreatorPdf(Creator):
    pass


class CreatorHtml(Creator):
    pass


class CreatorCbr(Creator):
    pass


class ComicThief:

    def __init__(self):
        self.fetcher = Fetcher()
        self.extractor = Extractor()
        self.creator = Creator()
        self.config = get_config(CONFIG)
        self.img_dir = self.config['SETTINGS'].get('img_dir', 'img')

    def fetch_comics_dict(self):
        page = self.fetcher.fetch_comic_list_page()
        return self.creator.make_comics_dict(self.extractor.extract_comic_links(page))

    def get_first_result(self, results):
        return sorted(results.items())[0][1]

    def search(self, keyword):
        comics_dict = self.fetch_comics_dict()
        results = self.creator.search_comics_dict(keyword, comics_dict)
        results_len = len(results)
        if results_len == 1:
            print('od razu pokazulemy subpage i epizody')
            subpage = self.fetcher.fetch_subpage(self.get_first_result(results))
            comics_dict = self.creator.make_comics_dict(self.extractor.extract_issues_list(subpage))
            print(comics_dict)
        elif results > 1:
            print('pokazujemy liste do sprecyzowania')
            print(results)
        else:
            print('Found nothing.')