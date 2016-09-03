'''
mediawiki module initialization
'''
from .mediawiki import (MediaWiki)
from .exceptions import (MediaWikiException, PageError,
                         RedirectError, DisambiguationError,
                         MediaWikiAPIURLError, HTTPTimeoutError)

__version__ = MediaWiki.version

__all__ = ['MediaWiki', 'PageError', 'RedirectError',
           'DisambiguationError', 'MediaWikiAPIURLError',
           'HTTPTimeoutError']
