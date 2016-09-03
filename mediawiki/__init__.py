from .mediawiki import (MediaWiki)
from .exceptions import (MediaWikiException, PageError,
                         RedirectError, DisambiguationError,
                         MediaWikiAPIURLError, HTTPTimeoutError)

__version__ = MediaWiki.get_version()

__all__ = ['MediaWiki', 'PageError', 'RedirectError',
           'DisambiguationError', 'MediaWikiAPIURLError',
           'HTTPTimeoutError']
