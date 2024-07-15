"""
mediawiki module initialization
"""

from mediawiki.configuraton import URL, VERSION
from mediawiki.exceptions import (
    DisambiguationError,
    HTTPTimeoutError,
    MediaWikiAPIURLError,
    MediaWikiCategoryTreeError,
    MediaWikiException,
    MediaWikiForbidden,
    MediaWikiGeoCoordError,
    MediaWikiLoginError,
    PageError,
    RedirectError,
)
from mediawiki.mediawiki import MediaWiki
from mediawiki.mediawikipage import MediaWikiPage

__author__ = "Tyler Barrus"
__maintainer__ = "Tyler Barrus"
__email__ = "barrust@gmail.com"
__license__ = "MIT"
__version__ = VERSION
__credits__ = ["Jonathan Goldsmith"]
__url__ = URL
__bugtrack_url__ = f"{__url__}/issues"
__download_url__ = f"{__url__}/tarball/v{__version__}"

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
    "MediaWikiForbidden",
]
