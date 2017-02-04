# -*- coding:utf-8 -*-

import os
import shutil
import unittest
from pathlib import Path

from config import (
    get_config,
    CONFIG
)
from extractor import Extractor
from fetcher import Fetcher
from creator import CreatorCbz
from main import ComicThief


class TestAll(unittest.TestCase):

    def setUp(self):
        self.config = get_config(CONFIG)
        self.img_dir = self.config['SETTINGS'].get('img_dir', 'img')
        self.output_dir = self.config['SETTINGS'].get('output_dir', 'comics')
        self.tests_output_dir = self.config['SETTINGS'].get('tests_output_dir', 'tests')
        self.fetcher = Fetcher()
        self.extractor = Extractor()
        self.creator = CreatorCbz()
        self.test_cwd = Path(Path.cwd(), self.tests_output_dir)
        self.ct = ComicThief(root_path=self.test_cwd)
        self.comic_name = 'Lobo'
        self.episode_name = "Lobo #5"
        self.episode_url = "http://www.readcomics.tv/lobo/chapter-5/full"

    def fetch_comics_dict(self):
        page = self.fetcher.fetch_comic_list_page()
        return self.creator.make_comics_dict(self.extractor.extract_comic_links(page))

    def test_fetch_default_comic_list_page(self):
        page = self.fetcher.fetch_comic_list_page()
        self.assertEqual(page.status_code, 200)

    def test_fetch_content(self):
        comics_dict = self.fetch_comics_dict()
        self.assertTrue(comics_dict)

    def test_search_comic(self):
        comics_dict = self.fetch_comics_dict()
        self.assertTrue(self.creator.search_comics_dict(self.comic_name, comics_dict))

    def test_search_and_fetch_subcontent(self):
        comics_dict = self.fetch_comics_dict()
        lobo_results = self.creator.search_comics_dict(self.comic_name, comics_dict)
        subpage = self.fetcher.fetch_subpage(self.ct.get_first_result(lobo_results))
        self.assertEqual(subpage.status_code, 200)
        comics_dict = self.creator.make_comics_dict(self.extractor.extract_issues_list(subpage))
        self.assertTrue(comics_dict)

    def test_fetch_image_links_from_subpage(self):
        subpage = self.fetcher.fetch_subpage(self.episode_url)
        images_list = self.extractor.extract_images_list(subpage)
        self.assertTrue(images_list)

    def test_download_images_list(self):
        subpage = self.fetcher.fetch_subpage(self.episode_url)
        images_list = self.extractor.extract_images_list(subpage)
        images_download_path = Path(self.test_cwd, self.output_dir, self.episode_name, self.img_dir)

        self.fetcher.download_images_list(
            Path(self.test_cwd,
                 self.output_dir,
                 self.episode_name,
                 self.img_dir),
            images_list)
        completed_files = os.listdir(images_download_path)

        self.assertTrue(images_download_path.exists())
        self.assertGreaterEqual(len(completed_files), len(images_list))

    def test_create_cbz_file(self):

        result = self.ct.exact_search(self.comic_name)
        episode_url = result.get(self.episode_name)
        if episode_url:
            self.ct.download_episode(episode_url, self.episode_name)

        self.assertTrue(
            Path(self.test_cwd,
                 self.output_dir,
                 self.episode_name,
                 "{}.cbz".format(self.episode_name)).exists())

    def tearDown(self):
        if self.test_cwd.exists():
            shutil.rmtree(self.test_cwd)


if __name__ == '__main__':
    unittest.main()
