"""
MediaWiki Exceptions
"""
from typing import List, Optional

from mediawiki.utilities import str_or_unicode

ODD_ERROR_MESSAGE = (
    "This should not happen. If the MediaWiki site you are "
    "querying is available, then please report this issue on "
    "GitHub: github.com/barrust/mediawiki"
)


class MediaWikiBaseException(Exception):
    """Base MediaWikiException

    Args:
        message: The message of the exception"""

    def __init__(self, message: str):
        self._message = message
        super().__init__(self.message)

    def __unicode__(self):
        return self.message

    def __str__(self):
        return str_or_unicode(self.__unicode__())

    @property
    def message(self) -> str:
        """str: The MediaWiki exception message"""
        return self._message


class MediaWikiException(MediaWikiBaseException):
    """MediaWiki Exception Class

    Args:
        error (str): The error message that the MediaWiki site returned"""

    def __init__(self, error: str):
        self._error = error
        msg = ('An unknown error occurred: "{}". Please report it on GitHub!').format(self.error)
        super().__init__(msg)

    @property
    def error(self) -> str:
        """str: The error message that the MediaWiki site returned"""
        return self._error


class PageError(MediaWikiBaseException):
    """Exception raised when no MediaWiki page matched a query

    Args:
        title (str): Title of the page
        pageid (int): MediaWiki page id of the page"""

    def __init__(self, title: Optional[str] = None, pageid: Optional[int] = None):
        if title:
            self._title = title
            msg = ('"{}" does not match any pages. Try another query!').format(self.title)
        elif pageid:
            self._pageid = pageid
            msg = ('Page id "{}" does not match any pages. Try another id!').format(self.pageid)
        else:
            self._title = ""
            msg = ('"{}" does not match any pages. Try another query!').format(self.title)
        super().__init__(msg)

    @property
    def title(self) -> str:
        """str: The title that caused the page error"""
        return self._title

    @property
    def pageid(self) -> int:
        """int: The page id that caused the page error"""
        return self._pageid


class RedirectError(MediaWikiBaseException):
    """ Exception raised when a page title unexpectedly resolves to
        a redirect

        Args:
            title (str): Title of the page that redirected
        Note:
            This should only occur if both auto_suggest and redirect \
            are set to **False** """

    def __init__(self, title: str):
        self._title = title
        msg = (
            '"{}" resulted in a redirect. Set the redirect property to True ' "to allow automatic redirects."
        ).format(self.title)

        super().__init__(msg)

    @property
    def title(self) -> str:
        """str: The title that was redirected"""
        return self._title


class DisambiguationError(MediaWikiBaseException):
    """ Exception raised when a page resolves to a Disambiguation page

        Args:
            title (str): Title that resulted in a disambiguation page
            may_refer_to (list): List of possible titles
            url (str): Full URL to the disambiguation page
            details (dict): A list of dictionaries with more information of \
                            possible results
        Note:
            `options` only includes titles that link to valid \
            MediaWiki pages """

    def __init__(self, title: str, may_refer_to: List[str], url: str, details: Optional[List[str]] = None):
        self._title = title
        self._unordered_options = may_refer_to
        self._options = sorted(may_refer_to)
        self._details = details
        self._url = url
        msg = ('\n"{}" may refer to: \n  ' "{}").format(self.title, "\n  ".join(self.options))
        super().__init__(msg)

    @property
    def url(self) -> str:
        """str: The url, if possible, of the disambiguation page"""
        return self._url

    @property
    def title(self) -> str:
        """str: The title of the page"""
        return self._title

    @property
    def options(self) -> List[str]:
        """list: The list of possible page titles"""
        return self._options

    @property
    def unordered_options(self) -> List[str]:
        """list: The list of possible page titles, un-sorted in an attempt to get them as they showup on the page"""
        return self._unordered_options

    @property
    def details(self) -> Optional[List[str]]:
        """list: The details of the proposed non-disambigous pages"""
        return self._details


class HTTPTimeoutError(MediaWikiBaseException):
    """Exception raised when a request to the Mediawiki site times out.

    Args:
        query (str): The query that timed out"""

    def __init__(self, query: str):
        self._query = query
        msg = (
            'Searching for "{}" resulted in a timeout. '
            "Try again in a few seconds, and ensure you have rate limiting "
            "set to True."
        ).format(self.query)
        super().__init__(msg)

    @property
    def query(self) -> str:
        """str: The query that timed out"""
        return self._query


class MediaWikiAPIURLError(MediaWikiBaseException):
    """Exception raised when the MediaWiki server does not support the API

    Args:
        api_url (str): The API URL that was not recognized"""

    def __init__(self, api_url: str):
        self._api_url = api_url
        msg = f"{self.api_url} is not a valid MediaWiki API URL"
        super().__init__(msg)

    @property
    def api_url(self) -> str:
        """str: The api url that raised the exception"""
        return self._api_url


class MediaWikiGeoCoordError(MediaWikiBaseException):
    """ Exceptions to handle GeoData exceptions

        Args:
            error (str): Error message from the MediaWiki site related to \
                         GeoCoordinates """

    def __init__(self, error: str):
        self._error = error
        msg = (
            "GeoData search resulted in the following error: {}"
            " - Please use valid coordinates or a proper page title."
        ).format(self.error)
        super().__init__(msg)

    @property
    def error(self) -> str:
        """str: The error that was thrown when pulling GeoCoordinates"""
        return self._error


class MediaWikiCategoryTreeError(MediaWikiBaseException):
    """Exception when the category tree is unable to complete for an unknown
    reason

    Args:
        category (str): The category that threw an exception"""

    def __init__(self, category: str):
        self._category = category
        msg = (
            "Categorytree threw an exception for trying to get the "
            "same category '{}' too many times. Please try again later "
            "and perhaps use the rate limiting "
            "option."
        ).format(self._category)
        super().__init__(msg)

    @property
    def category(self) -> str:
        """ str: The category that threw an exception during category tree \
                 generation """
        return self._category


class MediaWikiLoginError(MediaWikiBaseException):
    """Exception raised when unable to login to the MediaWiki site

    Args:
        error (str): The error message that the MediaWiki site returned"""

    def __init__(self, error: str):
        self._error = error
        super().__init__(error)

    @property
    def error(self) -> str:
        """str: The error message that the MediaWiki site returned"""
        return self._error
