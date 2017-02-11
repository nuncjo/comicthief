# -*- coding:utf-8 -*-

from collections import namedtuple
from pathlib import Path

from .cache import pickle_cache
from .config import (
    get_config,
    CONFIG
)

from .extractor import Extractor
from .fetcher import Fetcher
from .creator import CreatorCbz


class ComicThief:

    def __init__(self, root_path=None):
        self.fetcher = Fetcher()
        self.extractor = Extractor()
        self.creator = CreatorCbz()
        self.config = get_config(CONFIG)
        self.img_dir = self.config['SETTINGS'].get('img_dir', 'img')
        self.output_dir = self.config['SETTINGS'].get('output_dir', 'comics')
        self.cwd = root_path or Path.cwd()

    @pickle_cache(3600)
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
            print('\n'.join(found.results_dict.keys()))
            return found.results_dict
        else:
            print('Found nothing.')

    def exact_search(self, keyword):
        found = self.find_results(keyword, exact=True)
        if found.results_len == 1:
            subpage = self.fetcher.fetch_subpage(self.get_first_result(found.results_dict))
            episodes = self.creator.make_comics_dict(self.extractor.extract_issues_list(subpage))
            print('\n'.join(episodes.keys()))
            return episodes
        else:
            print('Found nothing.')

    def download_episode(self, url, name):
        name = name.replace('/', '_')
        subpage = self.fetcher.fetch_subpage(url + '/full')
        images_list = self.extractor.extract_images_list(subpage)
        self.fetcher.download_images_list(Path(self.cwd, self.output_dir, name, self.img_dir), images_list)
        self.creator.create(Path(self.cwd, self.output_dir, name), self.img_dir, name)
        print('Episode downloaded.')
