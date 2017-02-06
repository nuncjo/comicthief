# -*- coding:utf-8 -*-

from lxml import html

from .config import WithConfig


class Extractor(WithConfig):

    def extract_comic_links(self, page, service='default'):
        tree = html.fromstring(page.content)
        return tree.xpath(self.config['COMICS_LIST_XPATH'].get(service))

    def extract_issues_list(self, page, service='default'):
        tree = html.fromstring(page.content)
        return tree.xpath(self.config['COMICS_SUBPAGE_XPATH'].get(service))

    def extract_images_list(self, page, service='default'):
        tree = html.fromstring(page.content)
        return tree.xpath(self.config['COMICS_IMAGES_XPATH'].get(service))
