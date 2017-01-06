# -*- coding:utf-8 -*-

import os
from pathlib import Path
import unittest
from .main import (
    Fetcher,
    Extractor,
    Creator,
    IMG_DIR
)


class TestAll(unittest.TestCase):

    def setUp(self):
        self.fetcher = Fetcher()
        self.extractor = Extractor()
        self.creator = Creator()

    def fetch_comics_dict(self):
        page = self.fetcher.fetch_comic_list_page()
        return self.creator.make_comics_dict(self.extractor.extract_comic_links(page))

    def get_first_result(self, results):
        return sorted(results.items())[0][1]

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
        subpage = self.fetcher.fetch_subpage(self.get_first_result(lobo_results))
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
        subpage_url = "http://www.readcomics.tv/lobo/chapter-1/full"
        subpage = self.fetcher.fetch_subpage(subpage_url)
        images_list = self.extractor.extract_images_list(subpage)
        local_path = './comics/test/'
        self.fetcher.download_images_list(local_path, images_list)
        completed_files = next(os.walk(str(Path(local_path, IMG_DIR))))[2] #os.listdir
        self.assertGreaterEqual(len(completed_files), len(images_list))

    def test_assemble_and_create_html_file(self):
        local_path = './comics/test/'
        file_name = 'test.html'
        self.creator.create_comic_html_file(local_path, file_name)
        self.assertTrue(Path(local_path, file_name).exists())

    def test_make_pdf_from_list(self):
        local_path = './comics/test/'
        file_name = 'test.pdf'
        images_paths_list = self.creator.make_comic_images_paths_list(local_path)
        self.creator.make_pdf_from_images_list(images_paths_list, local_path, file_name)
        self.assertTrue(Path(local_path, file_name).exists())


if __name__ == '__main__':
    unittest.main()
