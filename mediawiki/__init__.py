"""
mediawiki module initialization
"""
from __future__ import unicode_literals, absolute_import
from .mediawiki import MediaWiki, URL, VERSION
from .mediawikipage import MediaWikiPage
from .exceptions import (
    MediaWikiException,
    PageError,
    MediaWikiGeoCoordError,
    RedirectError,
    DisambiguationError,
    MediaWikiAPIURLError,
    HTTPTimeoutError,
    MediaWikiCategoryTreeError,
    MediaWikiLoginError,
)

__author__ = "Tyler Barrus"
__maintainer__ = "Tyler Barrus"
__email__ = "barrust@gmail.com"
__license__ = "MIT"
__version__ = VERSION
__credits__ = ["Jonathan Goldsmith"]
__url__ = URL
__bugtrack_url__ = "{0}/issues".format(URL)

__all__ = [
    "MediaWiki",
    "MediaWikiPage",
    "PageError",
    "RedirectError",
    "MediaWikiException",
    "DisambiguationError",
    "MediaWikiAPIURLError",
    "HTTPTimeoutError",
    "MediaWikiGeoCoordError",
    "MediaWikiCategoryTreeError",
    "MediaWikiLoginError",
]
