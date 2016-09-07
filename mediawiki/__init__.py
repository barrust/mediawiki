'''
mediawiki module initialization
'''
from .mediawiki import (MediaWiki)
from .exceptions import (MediaWikiException, PageError,
                         RedirectError, DisambiguationError,
                         MediaWikiAPIURLError, HTTPTimeoutError)

__author__ = "Tyler Barrus"
__maintainer__ = "Tyler Barrus"
__email__ = "barrust@gmail.com"
__license__ = "MIT"
__version__ = MediaWiki.get_version()
__credits__ = ["Jonathan Goldsmith"]

__all__ = ['MediaWiki', 'PageError', 'RedirectError',
           'DisambiguationError', 'MediaWikiAPIURLError',
           'HTTPTimeoutError']
