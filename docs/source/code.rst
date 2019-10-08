.. _api:

MediaWiki Documentation
***********************

Here you can find the full developer API for the mediawiki project.


Functions and Classes
===============================

MediaWiki
+++++++++++++++++++++++++++++++

.. autoclass:: mediawiki.MediaWiki
    :members: version, api_version, extensions, rate_limit,
              rate_limit_min_wait, timeout, language, user_agent, api_url,
              memoized, clear_memoized, refresh_interval, set_api_url,
              supported_languages, random, categorytree, page, wiki_request

    .. automethod:: mediawiki.MediaWiki.login(username, password)
    .. automethod:: mediawiki.MediaWiki.suggest(query)
    .. automethod:: mediawiki.MediaWiki.search(query, results=10, suggestion=False)
    .. automethod:: mediawiki.MediaWiki.allpages(query='', results=10)
    .. automethod:: mediawiki.MediaWiki.summary(title, sentences=0, chars=0, auto_suggest=True, redirect=True)
    .. automethod:: mediawiki.MediaWiki.geosearch(latitude=None, longitude=None, radius=1000, title=None, auto_suggest=True, results=10)
    .. automethod:: mediawiki.MediaWiki.prefixsearch(prefix, results=10)
    .. automethod:: mediawiki.MediaWiki.opensearch(query, results=10, redirect=True)
    .. automethod:: mediawiki.MediaWiki.categorymembers(category, results=10, subcategories=True)


MediaWikiPage
+++++++++++++++++++++++++++++++

.. autoclass:: mediawiki.MediaWikiPage
    :members:

Exceptions
===============================

.. automodule:: mediawiki.exceptions
    :members:

Indices and tables
==================

* :ref:`home`
* :ref:`quickstart`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
