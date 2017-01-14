.. _home:

MediaWiki
=========
.. image:: https://badge.fury.io/py/pymediawiki.svg
    :target: https://badge.fury.io/py/pymediawiki
.. image:: https://travis-ci.org/barrust/mediawiki.svg?branch=master
    :target: https://travis-ci.org/barrust/mediawiki
    :alt: Build Status
.. image:: https://coveralls.io/repos/github/barrust/mediawiki/badge.svg?branch=master
    :target: https://coveralls.io/github/barrust/mediawiki?branch=master
    :alt: Test Coverage
.. image:: https://api.codacy.com/project/badge/Grade/afa87d5f5b6e4e66b78e15dedbc097ec
    :target: https://www.codacy.com/app/barrust/mediawiki?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=barrust/mediawiki&amp;utm_campaign=Badge_Grade
    :alt: Codacy Review
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://opensource.org/licenses/MIT/
    :alt: License

MediaWiki is a python library to help pull information from MediaWiki sites
using the MediaWiki API. It provides a simple and, hopefully, intuitive
manner of accessing the data and returning it in standard python data types.

MediaWiki wraps the `MediaWiki API <https://www.mediawiki.org/wiki/API>`_
so you can focus on leveraging your favorite MediaWiki site's data,
not getting it. Please check out the code on
`github <https://www.github.com/barrust/mediawiki>`_!

.. code: python

>>> from mediawiki import (MediaWiki)
>>> wikipedia = MediaWiki()
>>> wikipedia.summary('Wikipedia')
# Wikipedia (/ˌwɪkɨˈpiːdiə/ or /ˌwɪkiˈpiːdiə/ WIK-i-PEE-dee-ə) is a collaboratively edited, multilingual, free Internet encyclopedia supported by the non-profit Wikimedia Foundation...


Go to the :ref:`quickstart` to start using ``mediawiki`` now, or see the :ref:`api`.

Indices and tables
******************

* :ref:`api`
* :ref:`quickstart`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
