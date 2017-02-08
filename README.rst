ComicThief
========================



.. image:: https://codecov.io/gh/nuncjo/comicthief/branch/master/graph/badge.svg?branch=master
    :target: https://codecov.io/github/nuncjo/comicthief
    :alt: codecov.io
    

Comic Books Scraper. Easy download comics and make .cbz files.

Should work on Python versions 3.4+ on Linux and also on Windows/MacOS (but not tested yet).

Downloads comics from `Readcomics.tv <http://www.readcomics.tv/>`_.

Download and install ComicThief by:

.. code-block:: bash

    $ pip3 install ComicThief
    or
    $ python3 setup.py install -r requirements.txt

Use as comand line utility:
----------------

Copy *ct.py* wherever You want.

Search comic books.

.. code-block:: bash

    $ python3 ct.py -s "Name"

Type if there is more than one result. List of episodes will appear.

.. code-block:: bash

    $ python3 ct.py -xs "Exact name"

Type to download selected episode.

.. code-block:: bash

    $ python3 ct.py -xs "Exact name" -e "Episode name #1"

Go to "comics" directory, there it is!

Use as library:
----------------

.. code-block:: python

    from ComicThief.main import ComicThief

    ct = ComicThief()
    result = ct.exact_search("Lobo")
    episode_url = result.get("Lobo #1")

    if episode_url:
        ct.download_episode(episode_url, "Lobo #1")
..

