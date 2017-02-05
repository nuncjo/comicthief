ComicThief
========================

Comic Books Scraper. Easy download comics and make .cbz files.

Downloads comics from `Readcomics.tv <http://www.readcomics.tv/>`_.

Download and install ComicThief by *python3 setup.py install -r requirements.txt*

Use as comand line utility:
----------------

1) Copy *ct.py* wherever You want.

2) Type *python3 ct.py -s "Name"* to search comic books.

3) Type *python3 ct.py -xs "Exact name"* if there is more than one result. List of episodes will appear.

4) Type *python3 ct.py -xs "Exact name" -e "Episode name #1"* to download selected episode.

5) Go to "comics" directory, there it is!

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

