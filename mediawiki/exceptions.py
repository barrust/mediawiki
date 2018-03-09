'''
MediaWiki Exceptions
'''
from __future__ import (unicode_literals, absolute_import)
from .utilities import (str_or_unicode)


ODD_ERROR_MESSAGE = ('This should not happen. If the MediaWiki site you are '
                     'querying is available, then please report this issue on '
                     'GitHub: github.com/barrust/mediawiki')


class MediaWikiBaseException(Exception):
    ''' Base MediaWikiException '''
    def __init__(self, message):
        self.message = message
        super(MediaWikiBaseException, self).__init__(self.message)

    def __unicode__(self):
        return self.message

    def __str__(self):
        return str_or_unicode(self.__unicode__())


class MediaWikiException(MediaWikiBaseException):
    ''' MediaWiki Exception Class '''

    def __init__(self, error):
        self._error = error
        msg = ('An unknown error occured: "{0}". Please report '
               'it on GitHub!').format(self.error)
        super(MediaWikiException, self).__init__(msg)

    @property
    def error(self):
        """ The error message that the MediaWiki site returned

        :getter: Returns the raised error message
        :type: str """
        return self._error


class PageError(MediaWikiBaseException):
    ''' Exception raised when no MediaWiki page matched a query '''

    def __init__(self, title=None, pageid=None):
        if title:
            self._title = title
            msg = ('"{0}" does not match any pages. Try another '
                   'query!').format(self.title)
        elif pageid:
            self._pageid = pageid
            msg = ('Page id "{0}" does not match any pages. Try '
                   'another id!').format(self.pageid)
        else:
            self._title = ''
            msg = ('"{0}" does not match any pages. Try another '
                   'query!').format(self.title)
        super(PageError, self).__init__(msg)

    @property
    def title(self):
        """ The title that caused the page error

        :getter: Returns the title that caused the page error
        :type: str """
        return self._title

    @property
    def pageid(self):
        """ The title that caused the page error

        :getter: Returns the pageid that caused the page error
        :type: str """
        return self._pageid


class RedirectError(MediaWikiBaseException):
    ''' Exception raised when a page title unexpectedly resolves to
    a redirect

    .. note:: This should only occur if both auto_suggest and redirect \
    are set to **False** '''

    def __init__(self, title):
        self._title = title
        msg = ('"{0}" resulted in a redirect. Set the redirect '
               'property to True to allow automatic '
               'redirects.').format(self.title)

        super(RedirectError, self).__init__(msg)

    @property
    def title(self):
        """ The title that was redirected

        :getter: Returns the title that was a redirect
        :type: str """
        return self._title


class DisambiguationError(MediaWikiBaseException):
    ''' Exception raised when a page resolves to a Disambiguation page

    The `options` property contains a list of titles of MediaWiki
    pages to which the query may refer

    .. note:: `options` only includes titles that link to valid \
    MediaWiki pages '''

    def __init__(self, title, may_refer_to, url, details=None):
        self._title = title
        self._options = sorted(may_refer_to)
        self._details = details
        self._url = url
        msg = ('\n"{0}" may refer to: \n  '
               '{1}').format(self.title, '\n  '.join(self.options))
        super(DisambiguationError, self).__init__(msg)

    @property
    def url(self):
        """ The url, if possible, of the disambiguation page

        :getter: Returns the url for the page
        :type: str """
        return self._url

    @property
    def title(self):
        """ The title of the page

        :getter: Returns the title of the disambiguation page
        :type: str """
        return self._title

    @property
    def options(self):
        """ The list of possible page titles

        :getter: Returns a list of `may refer to` pages
        :type: list(str) """
        return self._options

    @property
    def details(self):
        """ The details of the proposed non-disambigous pages

        :getter: Returns the disambiguous page information
        :type: list """
        return self._details


class HTTPTimeoutError(MediaWikiBaseException):
    ''' Exception raised when a request to the Mediawiki site times out. '''

    def __init__(self, query):
        self._query = query
        msg = ('Searching for "{0}" resulted in a timeout. Try '
               'again in a few seconds, and ensure you have rate '
               'limiting set to True.').format(self.query)
        super(HTTPTimeoutError, self).__init__(msg)

    @property
    def query(self):
        """ The query that timed out

        :getter: Returns the query that timed out
        :type: str """
        return self._query


class MediaWikiAPIURLError(MediaWikiBaseException):
    ''' Exception raised when the MediaWiki server does not support the API '''

    def __init__(self, api_url):
        self._api_url = api_url
        msg = '{0} is not a valid MediaWiki API URL'.format(self.api_url)
        super(MediaWikiAPIURLError, self).__init__(msg)

    @property
    def api_url(self):
        """ The api url that raised the exception

        :getter: Returns the attempted api url
        :type: str """
        return self._api_url


class MediaWikiGeoCoordError(MediaWikiBaseException):
    ''' Exceptions to handle GeoData exceptions '''

    def __init__(self, error):
        self._error = error
        msg = ('GeoData search resulted in the following '
               'error: {0} - Please use valid coordinates or a proper '
               'page title.').format(self.error)
        super(MediaWikiGeoCoordError, self).__init__(msg)

    @property
    def error(self):
        """ The error that was thrown when pulling GeoCoordinates

        :getter: The error message
        :type: str """
        return self._error


class MediaWikiCategoryTreeError(MediaWikiBaseException):
    ''' Exception when the category tree is unable to complete for an unknown
        reason '''

    def __init__(self, category):
        self._category = category
        msg = ("Categorytree threw an exception for trying to get the "
               "same category '{}' too many times. Please try again later "
               "and perhaps use the rate limiting "
               "option.").format(self._category)
        super(MediaWikiCategoryTreeError, self).__init__(msg)

    @property
    def category(self):
        """ The category that threw an exception during category tree \
            generation

        :getter: Returns the category that caused the exception
        :type: str """
        return self._category
