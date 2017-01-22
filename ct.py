# -*- coding:utf-8 -*-

from argparse import ArgumentParser
from main import ComicThief

OPTIONS = [
    (('-s', '--search'), {'help': 'search'}),
    (('-xs', '--xsearch'), {'help': 'exact search to narrow more than one result'}),
    (('-d', '--download'), {'help': 'download'}),
    (('-e', '--episode'),  {'help': 'choose episode', 'type': str}),
    (('-o', '--output'), {'help': 'output format html. pdf, cbr'}),
]


def add_arguments(parser):
    for option, kwargs in OPTIONS:
        parser.add_argument(*option, **kwargs)


def download_episode(episode):
    episode_url = result.get(episode)
    if episode_url:
        ct.download_episode(episode_url, episode)

if __name__ == '__main__':
    ct = ComicThief()
    parser = ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    if args.search:
        print('searching')
        results = ct.search(args.search)
        if results == 1 and args.episode:
            download_episode(args.episode)
    elif args.xsearch:
        result = ct.exact_search(args.xsearch)
        if args.episode:
            download_episode(args.episode)
