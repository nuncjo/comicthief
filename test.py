# -*- coding:utf-8 -*-

import os
from pathlib import Path
import unittest
from .config import get_config, CONFIG
from .main import (
    Fetcher,
    Extractor,
    CreatorCbz,
    ComicThief,
)


class TestAll(unittest.TestCase):

    def setUp(self):
        self.config = get_config(CONFIG)
        self.img_dir = self.config['SETTINGS'].get('img_dir', 'img')
        self.tests_output_dir = self.config['SETTINGS'].get('tests_output_dir', 'tests')
        self.fetcher = Fetcher()
        self.extractor = Extractor()
        self.creator = CreatorCbz()
        self.cwd = Path(Path.cwd(), self.tests_output_dir)
        self.ct = ComicThief(root_path=self.cwd)

    def fetch_comics_dict(self):
        page = self.fetcher.fetch_comic_list_page()
        return self.creator.make_comics_dict(self.extractor.extract_comic_links(page))

    def test_fetch_default_comic_list_page(self):
        page = self.fetcher.fetch_comic_list_page()
        self.assertEqual(page.status_code, 200)

    def test_fetch_content(self):
        comics_dict = self.fetch_comics_dict()
        self.assertTrue(bool(comics_dict))

    def test_search_comic(self):
        comics_dict = self.fetch_comics_dict()
        self.assertTrue(bool(self.creator.search_comics_dict('Marvel', comics_dict)))

    def test_search_and_fetch_subcontent(self):
        comics_dict = self.fetch_comics_dict()
        lobo_results = self.creator.search_comics_dict('Lobo', comics_dict)
        subpage = self.fetcher.fetch_subpage(self.ct.get_first_result(lobo_results))
        self.assertEqual(subpage.status_code, 200)
        comics_dict = self.creator.make_comics_dict(self.extractor.extract_issues_list(subpage))
        self.assertTrue(bool(comics_dict))

    def test_fetch_image_links_from_subpage(self):
        subpage_url = "http://www.readcomics.tv/lobo/chapter-1/full"
        subpage = self.fetcher.fetch_subpage(subpage_url)
        images_list = self.extractor.extract_images_list(subpage)
        self.assertTrue(bool(images_list))

    def test_download_image(self):
        file_path = self.fetcher.download_image(
            'http://www.readcomics.tv/images/manga/lobo/1/1.jpg',
            './comics/test/',
            'test_img.jpg'
        )
        self.assertTrue(file_path.exists())
        os.remove(str(file_path))

    def test_download_images_list(self):
        episode_url = "http://www.readcomics.tv/lobo/chapter-4/full"
        subpage = self.fetcher.fetch_subpage(episode_url)
        images_list = self.extractor.extract_images_list(subpage)
        self.fetcher.download_images_list(Path(self.cwd, "Lobo #4", self.img_dir), images_list)
        completed_files = os.listdir(str(Path(self.cwd, "Lobo #4", self.img_dir)))
        self.assertTrue(Path(self.cwd, "Lobo #4", self.img_dir).exists())
        self.assertGreaterEqual(len(completed_files), len(images_list))

    def test_create_cbz_file(self):
        result = self.ct.exact_search('Lobo')
        episode_url = result.get("Lobo #5")
        if episode_url:
            self.ct.download_episode(episode_url, "Lobo #5")
            tu skonczylem dokonczyc ten test oraz przerobic reszte
        self.assertTrue(Path(self.cwd, self.img_dir, "Lobo #5.cbz").exists())

    def tearDown(self):
        #TODO:usuwanie self.tests_output_dir
        pass


if __name__ == '__main__':
    unittest.main()
