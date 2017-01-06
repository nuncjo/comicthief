# -*- coding:utf-8 -*-

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, wait
import os
from urllib.parse import urlparse

import requests
from lxml import html
from PyQt5.QtCore import QPoint
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument, QImage, QPdfWriter, QPainter, QPageSize, QPagedPaintDevice
from PyQt5.QtWidgets import QApplication


COMICS_LIST = {'default': 'http://www.readcomics.tv/comic-list'}
COMICS_LIST_XPATH = {'default': '//div[@class="serie-box"]/ul/li/a'}
COMICS_SUBPAGE_XPATH = {'default': '//ul[@class="basic-list"]/li/a'}
COMICS_IMAGES_XPATH = {'default': '//div[@class="chapter-container"]/img/@src'}
IMG_DIR = 'img'
CWD = Path.cwd()

HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head></head>
<body>
  <div>{}</div>
</body>
</html>
'''


def name_fits(search_phrase, key):
    if key:
        return search_phrase.lower() in key.lower()


class Fetcher:

    def fetch_comic_list_page(self, service='default'):
        return requests.get(COMICS_LIST[service])

    def fetch_subpage(self, url):
        return requests.get(url)

    def prepare_ordered_filename(self, remote_path, order):
        file_name = os.path.split(remote_path)[-1]
        return "{}.{}".format(str(order), file_name.split('.')[1])

    def download_image(self, url, local_path, name):
        img = requests.get(url)
        download_path = Path(Path.cwd(), local_path, IMG_DIR, name)
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


class Extractor:

    def extract_comic_links(self, page, service='default'):
        tree = html.fromstring(page.content)
        return tree.xpath(COMICS_LIST_XPATH[service])

    def extract_issues_list(self, page, service='default'):
        tree = html.fromstring(page.content)
        return tree.xpath(COMICS_SUBPAGE_XPATH[service])

    def extract_images_list(self, page, service='default'):
        tree = html.fromstring(page.content)
        return tree.xpath(COMICS_IMAGES_XPATH[service])


class Creator:

    def make_comics_dict(self, hrefs):
        return {item.text: item.attrib.get('href') for item in hrefs}

    def search_comics_dict(self, search_phrase, comics_dict):
        return {key: value for key, value in comics_dict.items() if name_fits(search_phrase, key)}

    def make_comic_html(self, local_path):
        files = next(os.walk(str(Path(local_path, IMG_DIR))))[2]
        images_html = ''.join(['<img src="{}"/>'.format(str(Path(CWD, local_path, IMG_DIR, file)))
                               for file in sorted(files, key=lambda x: int(x.split('.')[0]))])
        return HTML_TEMPLATE.format(images_html)

    def make_comic_images_paths_list(self, local_path):
        files = next(os.walk(str(Path(local_path, IMG_DIR))))[2]
        images_paths_list = [str(Path(CWD, local_path, IMG_DIR, file))
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