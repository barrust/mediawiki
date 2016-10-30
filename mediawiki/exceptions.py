'''
MediaWiki Exceptions
'''
from __future__ import unicode_literals
import sys


ODD_ERROR_MESSAGE = ('This should not happen. Please report on '
                     'GitHub if the MediaWiki site is available: '
                     'github.com/barrust/mediawiki')


class MediaWikiBaseException(Exception):
    ''' Base MediaWikiException '''
    def __init__(self, message):
        self.message = message
        super(MediaWikiBaseException, self).__init__(self.message)

    def __unicode__(self):
        return self.message

    def __str__(self):
        if sys.version_info > (3, 0):
            return self.__unicode__()
        else:
            return self.__unicode__().encode('utf8')


class MediaWikiException(MediaWikiBaseException):
    ''' MediaWiki Exception Class '''

    def __init__(self, error):
        self.error = error
        msg = ('An unknown error occured: "{0}". Please report '
               'it on GitHub!').format(self.error)
        super(MediaWikiException, self).__init__(msg)


class PageError(MediaWikiBaseException):
    ''' Exception raised when no MediaWiki page matched a query '''

    def __init__(self, title=None, pageid=None):
        if title:
            self.title = title
            msg = (u'"{0}" does not match any pages. Try another '
                   'query!').format(self.title)
        elif pageid:
            self.pageid = pageid
            msg = (u'Page id "{0}" does not match any pages. Try '
                   'another id!').format(self.pageid)
        else:
            self.title = ''
            msg = (u'"{0}" does not match any pages. Try another '
                   'query!').format(self.title)
        super(PageError, self).__init__(msg)


class RedirectError(MediaWikiBaseException):
    ''' Exception raised when a page title unexpectedly resolves to
    a redirect

    .. note:: This should only occur if both auto_suggest and redirect \
    are set to **False**
    '''

    def __init__(self, title):
        self.title = title
        msg = (u'"{0}" resulted in a redirect. Set the redirect '
               'property to True to allow automatic '
               'redirects.').format(self.title)

        super(RedirectError, self).__init__(msg)


class DisambiguationError(MediaWikiBaseException):
    ''' Exception raised when a page resolves to a Disambiguation page

    The `options` property contains a list of titles of MediaWiki
    pages to which the query may refer

    .. note:: `options` only includes titles that link to valid \
    MediaWiki pages
    '''

    def __init__(self, title, may_refer_to, details=None):
        self.title = title
        self.options = sorted(may_refer_to)
        self.details = details
        msg = (u'\n"{0}" may refer to: \n  '
               '{1}').format(self.title, '\n  '.join(self.options))
        super(DisambiguationError, self).__init__(msg)


class HTTPTimeoutError(MediaWikiBaseException):
    ''' Exception raised when a request to the Mediawiki site times out. '''

    def __init__(self, query):
        self.query = query
        msg = (u'Searching for "{0}" resulted in a timeout. Try '
               'again in a few seconds, and ensure you have rate '
               'limiting set to True.').format(self.query)
        super(HTTPTimeoutError, self).__init__(msg)


class MediaWikiAPIURLError(MediaWikiBaseException):
    ''' Exception raised when the MediaWiki server does not support the API '''

    def __init__(self, api_url):
        self.api_url = api_url
        msg = '{0} is not a valid MediaWiki API URL'.format(self.api_url)
        super(MediaWikiAPIURLError, self).__init__(msg)


class MediaWikiGeoCoordError(MediaWikiBaseException):
    ''' Exceptions to handle GeoData exceptions '''

    def __init__(self, error):
        self.error = error
        msg = ('GeoData search resulted in the following '
               'error: {0} - Please use valid coordinates or a proper '
               'page title.').format(self.error)
        super(MediaWikiGeoCoordError, self).__init__(msg)
