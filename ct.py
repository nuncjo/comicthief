# -*- coding:utf-8 -*-

import sys
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

if __name__ == '__main__':
    """
    ct.py -s nazwa_komiksu <-szuka komiks i gdy znajdzie zwraca epizody
    ct.py -d nazwa_komiksu -e nazwa_epizodu -> sciaga dany epizod komiksu
    ct.py -d nazwa_komiksu -e -all -> sciaga wszystkie epizody komiksu
    """
    ct = ComicThief()
    parser = ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    if args.search:
        print('searching')
        results = ct.search(args.search)
        if args.episode:
            pass
    elif args.xsearch:
        result = ct.exact_search(args.xsearch)
        if args.episode:
            episode_url = result.get(args.episode)
            if episode_url:
                print(episode_url)
                ct.download_episode(episode_url, args.episode)

    # elif args.download:
    #     print('downloading')
    #     if args.output:
    #         print("outputing")
    #     if args.episode:
    #         print("outputing")

    print(sys.argv)
