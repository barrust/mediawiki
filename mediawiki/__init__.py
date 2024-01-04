"""
mediawiki module initialization
"""
from .exceptions import (
    DisambiguationError,
    HTTPTimeoutError,
    MediaWikiAPIURLError,
    MediaWikiCategoryTreeError,
    MediaWikiException,
    MediaWikiGeoCoordError,
    MediaWikiLoginError,
    PageError,
    RedirectError,
)
from .mediawiki import URL, VERSION, MediaWiki
from .mediawikipage import MediaWikiPage

__author__ = "Tyler Barrus"
__maintainer__ = "Tyler Barrus"
__email__ = "barrust@gmail.com"
__license__ = "MIT"
__version__ = VERSION
__credits__ = ["Jonathan Goldsmith"]
__url__ = URL
__bugtrack_url__ = "{0}/issues".format(__url__)
__download_url__ = "{0}/tarball/v{1}".format(__url__, __version__)

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
