.. _home:

MediaWiki
=========

MediaWiki is a python library to help pull information from MediaWiki sites
using the MediaWiki API. It provides a simple and, hopefully, intuitive
manner of accessing the data and returning it in standard python data types.

MediaWiki wraps the `MediaWiki API <https://www.mediawiki.org/wiki/API>`_
so you can focus on leveraging your favorite MediaWiki site's data,
not getting it.

.. code: python

>>> from mediawiki import (MediaWiki)
>>> wikipedia = MediaWiki()
>>> wikipedia.summary('Wikipedia')
# Wikipedia (/ˌwɪkɨˈpiːdiə/ or /ˌwɪkiˈpiːdiə/ WIK-i-PEE-dee-ə) is a collaboratively edited, multilingual, free Internet encyclopedia supported by the non-profit Wikimedia Foundation...


Go to the :ref:`quickstart` to start using ``mediawiki`` now, or see the :ref:`api`.

Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`api`
* :ref:`search`
