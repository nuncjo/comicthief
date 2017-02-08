# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open("requirements.txt", "rb"):
    requires = [i.strip() for i in f.read().decode("utf-8").split("\n")]


setup(
    name='ComicThief',
    version='0.1.8',
    description='Comic Books Scraper. Easy download comics and make .cbz files.',
    long_description=readme,
    author='Nuncjo',
    author_email='zoreander@gmail.com',
    url='https://github.com/nuncjo/comicthief',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    package_data={'': ['*.*']},
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    platforms=["Windows", "MacOS", "Unix"],
    install_requires=requires
)