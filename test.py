# -*- coding:utf-8 -*-

import os
from pathlib import Path
import unittest
from .fetcher import (
    fetch_comic_list_page,
    make_comics_dict,
    extract_comic_links,
    search_comics_dict,
    fetch_subpage,
    extract_issues_list,
    extract_images_list,
    download_image,
    download_images_list,
    make_comic_html,
    create_comic_html_file,
    make_pdf_from_html,
    make_pdf_from_images_list,
    make_comic_images_paths_list,
    IMG_DIR
)

#TODO: dekorator post mortem:http://stackoverflow.com/questions/4398967/python-unit-testing-automatically-running-the-debugger-when-a-test-fails
class TestFetcher(unittest.TestCase):

    def fetch_comics_dict(self):
        page = fetch_comic_list_page()
        return make_comics_dict(extract_comic_links(page))

    def get_first_result(self, results):
        return sorted(results.items())[0][1]

    def test_fetch_default_comic_list_page(self):
        page = fetch_comic_list_page()
        self.assertEqual(page.status_code, 200)

    def test_fetch_content(self):
        comics_dict = self.fetch_comics_dict()
        self.assertTrue(bool(comics_dict))

    def test_search_comic(self):
        comics_dict = self.fetch_comics_dict()
        self.assertTrue(bool(search_comics_dict('Marvel', comics_dict)))

    def test_search_and_fetch_subcontent(self):
        comics_dict = self.fetch_comics_dict()
        lobo_results = search_comics_dict('Lobo', comics_dict)
        subpage = fetch_subpage(self.get_first_result(lobo_results))
        self.assertEqual(subpage.status_code, 200)
        comics_dict = make_comics_dict(extract_issues_list(subpage))
        self.assertTrue(bool(comics_dict))

    def test_fetch_image_links_from_subpage(self):
        subpage_url = "http://www.readcomics.tv/lobo/chapter-1/full"
        subpage = fetch_subpage(subpage_url)
        images_list = extract_images_list(subpage)
        self.assertTrue(bool(images_list))

    def test_download_image(self):
        file_path = download_image(
            'http://www.readcomics.tv/images/manga/lobo/1/1.jpg',
            './comics/test/',
            'test_img.jpg'
        )
        self.assertTrue(file_path.exists())
        os.remove(str(file_path))

    def test_download_images_list(self):
        subpage_url = "http://www.readcomics.tv/lobo/chapter-1/full"
        subpage = fetch_subpage(subpage_url)
        images_list = extract_images_list(subpage)
        local_path = './comics/test/'
        download_images_list(local_path, images_list)
        completed_files = next(os.walk(str(Path(local_path, IMG_DIR))))[2]
        self.assertGreaterEqual(len(completed_files), len(images_list))

    def test_assemble_and_create_html_file(self):
        local_path = './comics/test/'
        file_name = 'test.html'
        create_comic_html_file(local_path, file_name)
        self.assertTrue(Path(local_path, file_name).exists())
        #TODO: sprawdzac istnienie pliku

    def test_make_pdf_from_html(self):
        local_path = './comics/test/'
        html = make_comic_html(local_path)
        make_pdf_from_html(html, local_path, 'test.pdf')
        #TODO: sprawdzac istnienie pliku

    def test_make_pdf_from_list(self):
        local_path = './comics/test/'
        images_paths_list = make_comic_images_paths_list(local_path)
        make_pdf_from_images_list(images_paths_list, local_path, 'test.pdf')
        # TODO: sprawdzac istnienie pliku


    #TODO: na teardown usuwac zawartosc katalogu testowego..

if __name__ == '__main__':
    unittest.main()
