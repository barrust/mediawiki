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
To installing `mediawiki`, simply clone the `repository on GitHub
<https://github.com/barrust/mediawiki>`__, then run from the folder:

::

    $ python setup.py install

`mediawiki` supports python versions 2.7 and 3.3 - 3.5

In the future, it would be great if `mediawiki` were available to install
using pip!


Automated Tests
------------------
To run automated tests, one must simply run the following command from the
downloaded folder:

::

    $ python setup.py test

Documentation
-------------

To build the documentation yourself run:

::

  $ pip install sphinx
  $ cd docs/
  $ make html

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
