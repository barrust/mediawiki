'''
mediawiki module initialization
'''
from .mediawiki import (MediaWiki, MediaWikiPage, URL, VERSION)
from .exceptions import (MediaWikiException, PageError, MediaWikiGeoCoordError,
                         RedirectError, DisambiguationError,
                         MediaWikiAPIURLError, HTTPTimeoutError)

__author__ = 'Tyler Barrus'
__maintainer__ = 'Tyler Barrus'
__email__ = 'barrust@gmail.com'
__license__ = 'MIT'
__version__ = VERSION
__credits__ = ['Jonathan Goldsmith']
__url__ = URL

__all__ = ['MediaWiki', 'PageError', 'RedirectError', 'MediaWikiException',
           'DisambiguationError', 'MediaWikiAPIURLError',
           'HTTPTimeoutError', 'MediaWikiGeoCoordError']
