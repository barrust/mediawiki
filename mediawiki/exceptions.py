# -*- coding: utf-8 -*-
'''
Global MediaWiki Exceptions
'''
from __future__ import unicode_literals
import sys


ODD_ERROR_MESSAGE = ("This shouldn't happen. Please report on "
                     "GitHub if the site is available: "
                     "github.com/barrust/mediawiki")


class MediaWikiException(Exception):
    ''' Base MediaWiki exception class '''

    def __init__(self, error):
        self.error = error

    def __unicode__(self):
        return ("An unknown error occured: \"{0}\". Please report "
                "it on GitHub!").format(self.error)

    def __str__(self):
        return self.__unicode__()


class PageError(MediaWikiException):
    ''' Exception raised when no MediaWiki page matched a query '''

    def __init__(self, title=None, pageid=None, *args):
        if title:
            self.title = title
        elif pageid:
            self.pageid = pageid
        else:
            self.title = ""

    def __unicode__(self):
        if hasattr(self, 'title'):
            return (u"\"{0}\" does not match any pages. Try another "
                    "query!").format(self.title)
        else:
            return (u"Page id \"{0}\" does not match any pages. Try "
                    "another id!").format(self.pageid)


class RedirectError(MediaWikiException):
    '''
        Exception raised when a page title unexpectedly resolves to
        a redirect
    '''

    def __init__(self, title):
        self.title = title

    def __unicode__(self):
        return (u"\"{0}\" resulted in a redirect. Set the redirect "
                "property to True to allow automatic redirects."
                ).format(self.title)


class DisambiguationError(MediaWikiException):
    '''
    Exception raised when a page resolves to a Disambiguation page

    The `options` property contains a list of titles of Wikipedia
    pages that the query may refer to

    Note: `options` does not include titles that do not link to a
    valid Wikipedia page
    '''

    def __init__(self, title, may_refer_to, details=None):
        self.title = title
        self.options = sorted(may_refer_to)
        self.details = details

    def __unicode__(self):
        return (u"\n\"{0}\" may refer to: \n  {1}"
                ).format(self.title, '\n  '.join(self.options))


class HTTPTimeoutError(MediaWikiException):
    '''
    Exception raised when a request to the Mediawiki site times out.
    '''

    def __init__(self, query):
        self.query = query

    def __unicode__(self):
        return (u"Searching for \"{0}\" resulted in a timeout. Try "
                "again in a few seconds, and make sure you have rate "
                "limiting set to True.").format(self.query)


class MediaWikiAPIURLError(MediaWikiException):
    ''' Exception raised when the MediaWiki server does not support the API '''

    def __init__(self, api_url):
        self.api_url = api_url

    def __unicode__(self):
        return "{0} is not a valid MediaWiki API URL".format(self.api_url)
