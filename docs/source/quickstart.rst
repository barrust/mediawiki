.. _quickstart:

MediaWiki Quickstart
====================

Quickly get started using the `mediawiki` python library. This page is designed
to help users understand the basics of using the `mediawiki` library.

To understand all possible parameters for each function and properties,
please see :ref:`api`.

.. toctree::

   quickstart

Install
^^^^^^^

Using pip
"""""""""

::

    $ pip install pymediawiki

From source
"""""""""""

Begin by installing Wikipedia: simply clone the
`repository on GitHub <https://github.com/barrust/mediawiki>`__,
then run the following command from the extracted folder:

::

    $ python setup.py install

Setup
^^^^^

Setting up the library is as easy as:

.. code: python

>>> from mediawiki import MediaWiki
>>> wikipedia = MediaWiki()


Change API URL
^^^^^^^^^^^^^^

To change the API URL, one can either set the url parameter

.. code: python

>>> from mediawiki import MediaWiki
>>> asoiaf = MediaWiki(url='http://awoiaf.westeros.org/api.php')

Or one can update an already setup MediaWiki object:

.. code: python

>>> wikipedia.set_api_url('http://awoiaf.westeros.org/api.php')


Searching
^^^^^^^^^

To search the MediaWiki site, it is as easy as calling one of the search
functions: `random`, `search`, `geosearch`, `opensearch`, or `prefixsearch`

random
""""""

Get a random page:

.. code: python

>>> wikipedia.random(pages=3)
# ['Sutton House, London', 'Iolaus violacea', 'Epigenetics & Chromatin']


search
""""""

Search for the provided title:

.. code: python

>>> wikipedia.search('washington', results=3)
# ['Washington', 'Washington, D.C.', 'List of Governors of Washington']

geosearch
"""""""""

Search based on geocoords (latitude/longitude):

.. code: python

>>> wikipedia.geosearch(latitude=0.0, longitude=0.0)
# ['Null Island', 'Mirdif 35']

opensearch
""""""""""

Search using the OpenSearch specification:

.. code: python

>>> wikipedia.opensearch('new york', results=1)
# [('New York', 'New York is a state in the Northeastern United States
and is the 27th-most extensive, fourth-most populous, and seventh-most
densely populated U.S.', 'https://en.wikipedia.org/wiki/New_York')]

prefixsearch
""""""""""""

Search for pages whose title has the defined prefix:

.. code: python

>>> wikipedia.prefixsearch('ba', results=5)
# ['Ba', 'Barack Obama', 'Baseball', "Bahá'í Faith", 'Basketball']


Page
^^^^

Load and access information from full MediaWiki pages. Load the page using
a title or page id and then access individual properties:

Initialize Page
"""""""""""""""

.. code: python

>>> p = wikipedia.page('grid compass')

title
"""""""""""

The revision id of the page

.. code: python

>>> p.title
# 'Grid Compass'


pageid
"""""""""""

The page id of the page

.. code: python

>>> p.pageid
# 3498511


revision_id
"""""""""""

The revision id of the page

.. code: python

>>> p.revision_id
# 740685101

parent_id
"""""""""""

The parent id  of the page

.. code: python

>>> p.parent_id
# 740682666

links
"""""

Links to other MediaWiki pages

.. code: python

>>> p.links
# ['Astronaut', 'Bill Moggridge', 'CP/M', 'Central processing unit',
'Dynabook', 'Electroluminescent display', 'FTP', 'Flip (form)',
'GRiD Systems Corporation', 'GRiD-OS', 'Gavilan SC', 'Grid compass',
'Hard drive', 'IEEE-488', 'Industrial design', 'Intel 8086',
'John Oliver Creighton', 'Kilobyte', 'Laptop computer',
'Magnetic bubble memory', 'Modem', 'NASA', 'Operating system',
'Osborne 1', 'Paratrooper', 'Patent rights', 'Perfect (film)',
'Portable computer', 'RadioShack', 'Riptide (American TV series)',
'STS-51-G', 'Sharp PC-5000', 'Space Shuttle Discovery',
'Tandy Corporation', 'U.S. government', 'United Kingdom',
'United States Army Special Forces', 'Xerox PARC']

Other Properties
""""""""""""""""

Other properties for a page include: `content`, `html`, `images`, `references`,
`categories`, `coordinates`, `redirects`, `backlinks`, `summary`, `sections`

Summarize
""""""""""""""""

Summarize a page using additional parameters:

.. code: python

>>> p.summarize(chars=50)
# The Grid Compass (written GRiD by its manufacturer...



Indices and tables
==================

* :ref:`home`
* :ref:`api`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
