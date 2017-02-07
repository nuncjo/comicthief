# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ComicThief',
    version='0.1.7',
    description='Comic Books Scraper. Easy download comics and make .cbz files.',
    long_description=readme,
    author='Nuncjo',
    author_email='zoreander@gmail.com',
    url='https://github.com/nuncjo/comicthief',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    package_data={'ComicThief': ['*.ini']},
    include_package_data=True
)