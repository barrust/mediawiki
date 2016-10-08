MediaWiki
=========

**mediawiki** is a python wrapper for the MediaWiki API. The goal is to allow
users to quickly and efficiently pull data from the MediaWiki site of their
choice instead of worrying about dealing directly with the API. As such,
it does not force the use of a particular MediaWiki site. It defaults to
`Wikipedia <http://www.wikipedia.org>`__ but other MediaWiki sites can
also be used.

**Note:** this library was designed for ease of use and simplicity, not for
advanced use. If you plan on doing serious scraping or automated requests,
please use
`Pywikipediabot <http://www.mediawiki.org/wiki/Manual:Pywikipediabot>`__
(or one of the other more advanced `Python MediaWiki API wrappers
<http://en.wikipedia.org/wiki/Wikipedia:Creating_a_bot#Python>`__),
which has a larger API, advanced rate limiting, and other features so we may
be considerate of the MediaWiki infrastructure.


Installation
------------------

Pip Installation:

::

    $ pip install pymediawiki

To install from source:

To install `mediawiki`, simply clone the `repository on GitHub
<https://github.com/barrust/mediawiki>`__, then run from the folder:

::

    $ python setup.py install

`mediawiki` supports python versions 2.7 and 3.3 - 3.5

Documentation
-------------

Documentation of the latest release is hosted on
`pythonhosted.org <https://pythonhosted.org/pymediawiki/>`__

To build the documentation yourself run:

::

    $ pip install sphinx
    $ cd docs/
    $ make html

Automated Tests
------------------

To run automated tests, one must simply run the following command from the
downloaded folder:

::

  $ python setup.py test


Quickstart
------------------

Setup and run a simple search:

.. code:: python

    >>> from mediawiki import MediaWiki
    >>> wikipedia = MediaWiki()
    >>> wikipedia.search('washington')





Changelog
------------------

Please see the `changelog
<https://github.com/barrust/mediawiki/blob/master/CHANGELOG.md>`__ for a list
of all changes.


License
-------

MIT licensed. See the `LICENSE file
<https://github.com/barrust/Wikipedia/blob/master/LICENSE>`__
for full details.
