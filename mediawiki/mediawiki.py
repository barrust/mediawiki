'''
MediaWiki class module
'''
# MIT License
# Author: Tyler Barrus (barrust@gmail.com)

from __future__ import unicode_literals
import sys
from datetime import (datetime, timedelta)
import time
from decimal import (Decimal, DecimalException)
import requests
from bs4 import BeautifulSoup
from .exceptions import (MediaWikiException, PageError,
                         RedirectError, DisambiguationError,
                         MediaWikiAPIURLError, HTTPTimeoutError,
                         MediaWikiGeoCoordError, ODD_ERROR_MESSAGE)
from .utilities import memoize

URL = 'https://github.com/barrust/mediawiki'
VERSION = '0.3.7'


class MediaWiki(object):
    ''' MediaWiki API Wrapper Instance

    :param url: API URL of the MediaWiki site; defaults to Wikipedia
    :type url: string
    :param lang: Language of the MediaWiki site; used to help change \
    API URL
    :type lang: string
    :param timeout: HTTP timeout setting; None means no timeout
    :type timeout: integer - seconds
    :param rate_limit: Use rate limiting to limit calls to the site
    :type rate_limit: Boolean
    :param rate_limit_wait: Amount of time to wait between requests
    :type rate_limit_wait: timedelta
    '''

    def __init__(self, url='http://en.wikipedia.org/w/api.php', lang='en',
                 timeout=None, rate_limit=False,
                 rate_limit_wait=timedelta(milliseconds=50)):
        ''' Init Function '''
        self._version = VERSION
        self._api_url = url
        self._lang = lang  # should this call self.language = lang?
        self._timeout = timeout
        self._user_agent = ('python-mediawiki/VERSION-{0}'
                            '/({1})/BOT').format(VERSION, URL)
        self._session = None
        self._rate_limit = rate_limit
        self._rate_limit_last_call = None
        self._min_wait = rate_limit_wait
        self._extensions = None
        self._api_version = None

        # for memoized results
        self._cache = dict()

        # call helper functions to get everything set up
        self._reset_session()
        try:
            self._get_site_info()
        except Exception:
            raise MediaWikiAPIURLError(url)

    # non-settable properties
    @property
    def version(self):
        ''' Version of the MediaWiki library

        :getter: Returns the version of the MediaWiki library
        :setter: Not settable
        :type: string
        '''
        return self._version

    @property
    def api_version(self):
        ''' API Version of the MediaWiki site

        :getter: Returns the API version of the MediaWiki site
        :setter: Not settable
        :type: string
        '''
        return '.'.join([str(x) for x in self._api_version])

    @property
    def extensions(self):
        '''Extensions installed on the MediaWiki site

        :getter: Returns a list of all extensions installed on the MediaWiki \
        site
        :setter: Not settable
        :type: list
        '''
        return sorted(list(self._extensions))

    # settable properties
    @property
    def rate_limit(self):
        ''' Turn on or off Rate Limiting

        :getter: Returns if rate limiting is used
        :setter: Turns on (**True**) or off (**False**) rate limiting
        :type: Boolean
        '''
        return self._rate_limit

    @rate_limit.setter
    def rate_limit(self, rate_limit):
        ''' Turn on or off rate limiting '''
        self._rate_limit = bool(rate_limit)
        self._rate_limit_last_call = None
        self.clear_memoized()

    @property
    def rate_limit_min_wait(self):
        ''' Time to wait between calls

        :getter: Returns the timedelta used to wait between API calls
        :setter: Sets the amount of time to wait between calls
        :type: timedelta

        .. note:: Only used if rate_limit is **True**
        '''
        return self._min_wait

    @rate_limit_min_wait.setter
    def rate_limit_min_wait(self, min_wait):
        ''' Set minimum wait to use for rate limiting '''
        self._min_wait = min_wait
        self._rate_limit_last_call = None

    @property
    def timeout(self):
        ''' Response timeout for API requests

        :getter: Returns the number of seconds to wait for a resonse
        :setter: Sets the number of seconds to wait for a response
        :type: integer or None

        .. note:: Use **None** for no response timeout
        '''
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        ''' Set request timeout in seconds (or fractions of a second) '''
        self._timeout = timeout

    @property
    def language(self):
        ''' API URL language

        :getter: Returns the set language of the API URL
        :setter: Changes the API URL to use the provided language code
        :type: string

        .. note:: Use correct language titles with the updated API URL

        .. note:: Some API URLs do not encode language; unable to update if \
        this is the case
        '''
        return self._lang

    @language.setter
    def language(self, lang):
        ''' Set the language to use; attempts to change the API URL '''
        lang = lang.lower()
        if self._lang == lang:
            return

        url = self._api_url
        tmp = url.replace('/{0}.'.format(self._lang), '/{0}.'.format(lang))

        self._api_url = tmp
        self._lang = lang
        self.clear_memoized()

    @property
    def user_agent(self):
        ''' User agent string

        :getter: Returns the user agent string used in requests
        :setter: Sets the user agent string; resets session
        :type: string

        .. note:: If using in as part of another project, this should be \
        changed
        '''
        return self._user_agent

    @user_agent.setter
    def user_agent(self, user_agent):
        ''' Set the new user agent string '''
        self._user_agent = user_agent
        self._reset_session()

    @property
    def api_url(self):
        '''API URL of the MediaWiki site

        :getter: Returns the API URL
        :setter: Not settable; see :py:func:`mediawiki.MediaWiki.set_api_url`
        :type: string
        '''
        return self._api_url

    @property
    def memoized(self):
        ''' Return the memoize cache

        :getter: Returns the cache used for memoization
        :setter: Not settable; see \
        :py:func:`mediawiki.MediaWiki.clear_memoized`
        :return: dict
        '''
        return self._cache

    # non-properties
    def set_api_url(self, api_url='http://en.wikipedia.org/w/api.php',
                    lang='en'):
        ''' Set the API URL and language

        :param api_url: API URL to use
        :type pages: string
        :param lang: Language of the API URL
        :type pages: string

        :raises `mediawiki.exceptions.MediaWikiAPIURLError`: \
        if the url is not a valid MediaWiki site
        '''
        self._api_url = api_url
        self._lang = lang
        try:
            self._get_site_info()
        except Exception:
            raise MediaWikiAPIURLError(api_url)
        self.clear_memoized()

    def _reset_session(self):
        ''' Set session information '''
        headers = {'User-Agent': self._user_agent}
        self._session = requests.Session()
        self._session.headers.update(headers)

    def clear_memoized(self):
        ''' Clear memoized (cached) values '''
        if hasattr(self, '_cache'):
            self._cache.clear()

    # non-setup functions
    def languages(self):
        ''' All supported language prefixes on the MediaWiki site

        :getter: Returns all supported language prefixes
        :setter: Not settable
        :returns: dict: prefix - local language name pairs
        '''
        res = self.wiki_request({'meta': 'siteinfo', 'siprop': 'languages'})
        return {lang['code']: lang['*'] for lang in res['query']['languages']}
    # end languages

    def random(self, pages=1):
        ''' Request a random page title or list of random titles

        :param pages: number of random pages to returns
        :type pages: integer
        :returns: A list of random page titles or a random page title \
        if pages = 1
        '''
        if pages is None or pages < 1:
            raise ValueError('Number of pages must be greater than 0')

        query_params = {'list': 'random', 'rnnamespace': 0, 'rnlimit': pages}

        request = self.wiki_request(query_params)
        titles = [page['title'] for page in request['query']['random']]

        if len(titles) == 1:
            return titles[0]

        return titles
    # end random

    @memoize
    def search(self, query, results=10, suggestion=False):
        ''' Search for similar titles

        :param query: Page title
        :param results: Number of pages to returns
        :type results: integer
        :param suggestion: Use suggestion
        :type suggestion: Boolean
        :returns: tuple (list results, suggestion) if suggestion is **True**; \
        list of results otherwise
        '''

        self._check_query(query, 'Query must be specified')

        search_params = {
            'list': 'search',
            'srprop': '',
            'srlimit': results,
            'srsearch': query
        }
        if suggestion:
            search_params['srinfo'] = 'suggestion'

        raw_results = self.wiki_request(search_params)

        self._check_error_response(raw_results, query)

        search_results = (d['title'] for d in raw_results['query']['search'])

        if suggestion:
            if raw_results['query'].get('searchinfo'):
                sug = raw_results['query']['searchinfo']['suggestion']
                return list(search_results), sug
            else:
                return list(search_results), None

        return list(search_results)
    # end search

    @memoize
    def suggest(self, query):
        ''' Gather suggestions based on the provided title or None if
        no suggestions found

        :param query: Page title
        :returns: string or None
        '''
        res, suggest = self.search(query, results=1, suggestion=True)
        try:
            title = suggest or res[0]
        except IndexError:  # page doesn't exist
            title = None
        return title
    # end suggest

    @memoize
    def geosearch(self, latitude=None, longitude=None, radius=1000,
                  title=None, auto_suggest=True, results=10):
        ''' Search for pages that relate to the provided geocoords or near
        the page

        :param latitude: Latitude geocoord
        :type latitude: Decimal, type that can be coaxed as Decimal, or None
        :param longitude: Longitude geocoord
        :type longitude: Decimal, type that can be coaxed as Decimal, or None
        :param radius: Radius around page or geocoords to pull back; in meters
        :type radius: integer
        :param title: Page title to use as a geocoordinate; this has \
        precedence over lat/long
        :type title: string
        :param auto_suggest: Auto-suggest the page title
        :type auto_suggest: Boolean
        :param results: Number of pages within the radius to return
        :type results: integer
        :returns: List of page titles
        '''

        def test_lat_long(val):
            ''' handle testing lat and long '''
            if not isinstance(val, Decimal):
                error = ('Latitude and Longitude must be specified either as '
                         'a Decimal or in formats that can be coerced into '
                         'a Decimal.')
                try:
                    return Decimal(val)
                except (DecimalException, TypeError):
                    raise ValueError(error)
            return val
        # end local function

        params = {
            'list': 'geosearch',
            'gsradius': radius,
            'gslimit': results
        }
        if title is not None:
            if auto_suggest:
                title = self.suggest(title)
            params['gspage'] = title
        else:
            lat = test_lat_long(latitude)
            lon = test_lat_long(longitude)
            params['gscoord'] = '{0}|{1}'.format(lat, lon)

        raw_results = self.wiki_request(params)

        self._check_error_response(raw_results, title)

        res = (d['title'] for d in raw_results['query']['geosearch'])

        return list(res)

    @memoize
    def opensearch(self, query, results=10, redirect=True):
        ''' Execute a MediaWiki opensearch request, similar to search box
        suggestions and conforming to the OpenSearch specification

        :param query: string to search for
        :type query: string
        :param results: number of pages within the radius to return
        :type results: integer
        :param redirect: If **False** return the redirect itself, otherwise \
        resolve redirects
        :type redirect: Boolean
        :returns: List of tuples: (Title, Summary, URL)
        '''

        self._check_query(query, 'Query must be specified')

        query_params = {
            'action': 'opensearch',
            'search': query,
            'limit': (100 if results > 100 else results),
            'redirects': ('resolve' if redirect else 'return'),
            'warningsaserror': True,
            'namespace': ''
        }

        results = self.wiki_request(query_params)

        self._check_error_response(results, query)

        res = list()
        for i, item in enumerate(results[1]):
            res.append((item, results[2][i], results[3][i],))

        return res

    @memoize
    def prefixsearch(self, prefix, results=10):
        ''' Perform a prefix search using the provided prefix string

        **Per the documentation:** "The purpose of this module is similar to
        action=opensearch: to take user input and provide the best-matching
        titles. Depending on the search engine backend, this might include
        typo correction, redirect avoidance, or other heuristics."

        :param prefix: prefix string to use for search
        :type prefix: string
        :param results: number of pages within the radius to return
        :type results: integer
        :returns: List of page titles
        '''

        self._check_query(prefix, 'Prefix must be specified')

        query_params = {
            'list': 'prefixsearch',
            'pssearch': prefix,
            'pslimit': ('max' if results > 500 else results),
            'psnamespace': 0,
            'psoffset': 0  # parameterize to skip to later in the list?
        }

        raw_results = self.wiki_request(query_params)

        self._check_error_response(raw_results, prefix)

        res = list()
        for rec in raw_results['query']['prefixsearch']:
            res.append(rec['title'])

        return res

    @memoize
    def summary(self, title, sentences=0, chars=0, auto_suggest=True,
                redirect=True):
        ''' Get the summary for the title in question

        :param title: Page title to summarize
        :type title: string
        :param sentences: Number of sentences to return in summary
        :type sentences: integer
        :param chars: Number of characters to return in summary
        :type chars: integer
        :param auto_suggest: Run auto-suggest on title before summarizing
        :type auto_suggest: Boolean
        :param redirect: Use page redirect on title before summarizing
        :type redirect: Boolean
        :returns: string

        .. note:: Precedence for parameters: sentences then chars; \
        if both are 0 then the entire first section is returned
        '''
        page_info = self.page(title, auto_suggest=auto_suggest,
                              redirect=redirect)
        return page_info.summarize(sentences, chars)

    @memoize
    def categorymembers(self, category, results=10, subcategories=True):
        ''' Get informaton about a category: pages and subcategories

        :param category: Category name
        :type category: string
        :param results: Number of result
        :type results: integer or None
        :param subcategories: Include subcategories (**True**) or not \
        (**False**)
        :type subcategories: Boolean

        .. note:: Set results to **None** to get all results
        '''
        self._check_query(category, 'Category must be specified')

        search_params = {
            'list': 'categorymembers',
            'cmprop': 'ids|title|type',
            'cmtype': ('page|subcat' if subcategories else 'page'),
            'cmlimit': (results if results is not None else 5000),
            'cmtitle': 'Category:{0}'.format(category)
        }
        pages = list()
        subcats = list()
        returned_results = 0
        finished = False
        last_continue = dict()
        while not finished:
            params = search_params.copy()
            params.update(last_continue)
            raw_results = self.wiki_request(params)

            self._check_error_response(raw_results, category)

            current_pull = len(raw_results['query']['categorymembers'])
            for rec in raw_results['query']['categorymembers']:
                if rec['type'] == 'page':
                    pages.append(rec['title'])
                elif rec['type'] == 'subcat':
                    tmp = rec['title']
                    if tmp.startswith('Category:'):
                        tmp = tmp[9:]
                    subcats.append(tmp)

            if 'continue' not in raw_results:
                break

            returned_results = returned_results + current_pull
            if results is None or (results - returned_results > 0):
                last_continue = raw_results['continue']
            else:
                finished = True

        # end while loop
        if subcategories:
            return pages, subcats
        else:
            return pages
    # end categorymembers

    # def categorytree(self, category, depth=5):
    #     ''' Generate the Category Tree data
    #
    #     :raises `NotImplementedError`: not implemented
    #
    #     .. todo:: implement
    #     '''
    #     raise NotImplementedError
    # end categorytree

    def page(self, title=None, pageid=None, auto_suggest=True, redirect=True,
             preload=False):
        ''' Get MediaWiki page based on the provided title or pageid

        :param title: Page title
        :type title: string or None
        :param pageid: MediaWiki page identifier
        :type pageid: integer or None
        :param auto-suggest: **True:** Allow page title auto-suggest
        :type auto_suggest: Boolean
        :param redirect: **True:** Follow page redirects
        :type redirect: Boolean
        :param preload: **True:** Load most page properties
        :type preload: Boolean

        .. note:: Title takes precedence over pageid if both are provided
        '''
        if (title is None or title.strip() == '') and pageid is None:
            raise ValueError('Either a title or a pageid must be specified')
        elif title:
            if auto_suggest:
                temp_title = self.suggest(title)
                if temp_title is None:  # page doesn't exist
                    raise PageError(title=title)
                else:
                    title = temp_title
            return MediaWikiPage(self, title, redirect=redirect,
                                 preload=preload)
        else:  # must be pageid
            return MediaWikiPage(self, pageid=pageid, preload=preload)
    # end page

    def wiki_request(self, params):
        ''' Make a request to the MediaWiki API using the given search
        parameters

        :param params: Dictionary of request parameters
        :type params: dict
        :returns: A parsed dict of the JSON response

        .. note:: Useful when wanting to query the MediaWiki site for some \
        value that is not part of the wrapper API
        '''

        params['format'] = 'json'
        if 'action' not in params:
            params['action'] = 'query'

        limit = self._rate_limit
        last_call = self._rate_limit_last_call
        if limit and last_call and last_call + self._min_wait > datetime.now():
            # call time to quick for rate limited api requests, wait
            wait_time = (last_call + self._min_wait) - datetime.now()
            time.sleep(int(wait_time.total_seconds()))

        req = self._get_response(params)

        if self._rate_limit:
            self._rate_limit_last_call = datetime.now()

        return req
    # end wiki_request

    # Protected functions
    def _get_site_info(self):
        '''
        Parse out the Wikimedia site information including
        API Version and Extensions
        '''
        response = self.wiki_request({
            'meta': 'siteinfo',
            'siprop': 'extensions|general'
        })

        # shouldn't a check for success be done here?

        gen = response['query']['general']['generator']
        api_version = gen.split(' ')[1].split('-')[0]

        major_minor = api_version.split('.')
        for i, item in enumerate(major_minor):
            major_minor[i] = int(item)
        self._api_version = tuple(major_minor)

        self._extensions = set()
        for ext in response['query']['extensions']:
            self._extensions.add(ext['name'])
    # end _get_site_info

    @staticmethod
    def _check_error_response(response, query):
        ''' check for default error messages and throw correct exception '''
        if 'error' in response:
            http_error = ['HTTP request timed out.', 'Pool queue is full']
            geo_error = ['Page coordinates unknown',
                         ('One of the parameters gscoord, gspage, gsbbox is '
                          'required'), 'Invalid coordinate provided']
            err = response['error']['info']
            if err in http_error:
                raise HTTPTimeoutError(query)
            elif err in geo_error:
                raise MediaWikiGeoCoordError(err)
            else:
                raise MediaWikiException(err)
        else:
            return

    @staticmethod
    def _check_query(value, message):
        ''' check if the query is 'valid' '''
        if value is None or value.strip() == '':
            raise ValueError(message)

    def _get_response(self, params):
        ''' wrap the call to the requests package '''
        return self._session.get(self._api_url, params=params,
                                 timeout=self._timeout).json(encoding='utf8')

# end MediaWiki class


# TODO: Should this be in it's own file?
class MediaWikiPage(object):
    '''
    MediaWiki Page Instance

    :param mediawiki: MediWiki class object from which to pull information
    :type mediawiki: MediaWiki class object
    :param title: Title of page to retrieve
    :type title: string or None
    :param pageid: MediaWiki site pageid to retrieve
    :type pageid: integer or None
    :param redirect: **True:** Follow redirects
    :type redirect: Boolean
    :param preload: **True:** Load most properties after getting page
    :type preload: Boolean
    :param original_title: Not to be used from the caller; used to help \
    follow redirects
    :type original_title: String

    :raises `mediawiki.exceptions.PageError`: if page provided does not exist
    :raises `mediawiki.exceptions.DisambiguationError`: if page provided \
    is a disambiguation page
    :raises `mediawiki.exceptions.RedirectError`: if redirect is **False** \
    and the pageid or title provided redirects to another page

    .. warning:: This should never need to be used directly! Please use \
    :func:`mediawiki.MediaWiki.page`
    '''

    def __init__(self, mediawiki, title=None, pageid=None,
                 redirect=True, preload=False, original_title=''):
        self.mediawiki = mediawiki
        self.url = None
        if title is not None:
            self.title = title
            self.original_title = original_title or title
        elif pageid is not None:
            self.pageid = pageid
        else:
            raise ValueError('Either a title or a pageid must be specified')

        self.__load(redirect=redirect, preload=preload)

        preload_props = ['content', 'summary', 'images', 'references', 'links',
                         'sections', 'redirects', 'coordinates', 'backlinks',
                         'categories']
        if preload:
            for prop in preload_props:
                getattr(self, prop)
        # end __init__

    def __repr__(self):
        ''' base repr function '''
        text = u'''<MediaWikiPage '{0}'>'''.format(self.title)
        encoding = sys.stdout.encoding or 'utf-8'
        if sys.version_info > (3, 0):
            return text.encode(encoding).decode(encoding)
        return text.encode(encoding)

    def __eq__(self, other):
        ''' base eq function '''
        try:
            return (
                self.pageid == other.pageid and
                self.title == other.title and
                self.url == other.url
            )
        except AttributeError:
            return False

    # Properties
    def _pull_content_revision_parent(self):
        ''' combine the pulling of these three properties '''
        if not getattr(self, '_content', False):
            query_params = {
                'prop': 'extracts|revisions',
                'explaintext': '',
                'rvprop': 'ids'
            }
            query_params.update(self.__title_query_param())
            request = self.mediawiki.wiki_request(query_params)
            page_info = request['query']['pages'][self.pageid]
            self._content = page_info['extract']
            self._revision_id = page_info['revisions'][0]['revid']
            self._parent_id = page_info['revisions'][0]['parentid']
        return self._content, self._revision_id, self._parent_id

    @property
    def content(self):
        ''' Page content

        :getter: Returns the page content
        :setter: Not settable
        :type: string

        .. note:: Side effect is to also get revision_id and parent_id
        '''
        if not getattr(self, '_content', False):
            self._pull_content_revision_parent()
        return self._content

    @property
    def revision_id(self):
        ''' Current revision id

        :getter: Returns the current revision id of the page
        :setter: Not settable
        :type: integer

        .. note:: Side effect is to also get content and parent_id
        '''
        if not getattr(self, '_revision_id', False):
            self._pull_content_revision_parent()
        return self._revision_id

    @property
    def parent_id(self):
        ''' Current parent id

        :getter: Returns the parent id of the page
        :setter: Not settable
        :type: integer

        .. note:: Side effect is to also get content and revision_id
        '''
        if not getattr(self, '_parent_id', False):
            self._pull_content_revision_parent()
        return self._parent_id

    @property
    def html(self):
        ''' Page HTML

        :getter: Returns the HTML of the page
        :setter: Not settable
        :type: string

        .. warning:: This can be slow for very large pages
        '''
        if not getattr(self, '_html', False):
            self._html = None
            query_params = {
                'prop': 'revisions',
                'rvprop': 'content',
                'rvlimit': 1,
                'rvparse': '',
                'titles': self.title
            }
            request = self.mediawiki.wiki_request(query_params)
            page = request['query']['pages'][self.pageid]
            self._html = page['revisions'][0]['*']
        return self._html

    @property
    def images(self):
        ''' Images on the page

        :getter: Returns the list of all image URLs on the page
        :setter: Not settable
        :type: list
        '''
        if not getattr(self, '_images', False):
            self._images = list()
            params = {
                'generator': 'images',
                'gimlimit': 'max',
                'prop': 'imageinfo',
                'iiprop': 'url'
                }
            for page in self._continued_query(params):
                if 'imageinfo' in page:
                    self._images.append(page['imageinfo'][0]['url'])
            self._images = sorted(self._images)
        return self._images

    @property
    def references(self):
        ''' External links, or references, listed on the page

        :getter: Returns the list of all external links
        :setter: Not settable
        :type: list

        .. note:: May include external links within page that are not \
        technically cited anywhere.
        '''
        if not getattr(self, '_references', False):
            params = {'prop': 'extlinks', 'ellimit': 'max'}
            self._references = list()
            for link in self._continued_query(params):
                if link['*'].startswith('http'):
                    url = link['*']
                else:
                    url = 'http:{0}'.format(link['*'])
                self._references.append(url)
            self._references = sorted(self._references)
        return self._references

    @property
    def categories(self):
        ''' Non-hidden categories on the page

        :getter: Returns the list of all non-hidden categories on the page
        :setter: Not settable
        :type: list
        '''
        if not getattr(self, '_categories', False):
            self._categories = list()
            params = {
                'prop': 'categories',
                'cllimit': 'max',
                'clshow': '!hidden'
                }
            for link in self._continued_query(params):
                if link['title'].startswith('Category:'):
                    self._categories.append(link['title'][9:])
                else:
                    self._categories.append(link['title'])
            self._categories = sorted(self._categories)
        return self._categories

    @property
    def coordinates(self):
        ''' GeoCoordinates of the place referenced

        :getter: Returns the geocoordinates of the place that the page \
        references
        :setter: Not settable
        :type: Tuple (Latitude, Logitude) or None if no geocoordinates present

        .. note: Requires the GeoData extension to be installed
        '''
        if not getattr(self, '_coordinates', False):
            self._coordinates = None
            params = {
                'prop': 'coordinates',
                'colimit': 'max',
                'titles': self.title
                }
            request = self.mediawiki.wiki_request(params)
            res = request['query']['pages'][self.pageid]
            if 'query' in request and 'coordinates' in res:
                self._coordinates = (Decimal(res['coordinates'][0]['lat']),
                                     Decimal(res['coordinates'][0]['lon']))
        return self._coordinates

    @property
    def links(self):
        ''' MediaWiki page links on a page

        :getter: Returns the list of all MediaWiki page links on this page
        :setter: Not settable
        :type: list
        '''
        if not getattr(self, '_links', False):
            self._links = list()
            params = {
                'prop': 'links',
                'plnamespace': 0,
                'pllimit': 'max'
                }
            for link in self._continued_query(params):
                self._links.append(link['title'])
            self._links = sorted(self._links)
        return self._links

    @property
    def redirects(self):
        ''' Redirects to the page

        :getter: Returns the list of all redirects to this page; \
        **i.e.,** the titles listed here will redirect to this page title
        :setter: Not settable
        :type: list
        '''
        if not getattr(self, '_redirects', False):
            self._redirects = list()
            params = {
                'prop': 'redirects',
                'rdprop': 'title',
                'rdlimit': 'max'
                }
            for link in self._continued_query(params):
                self._redirects.append(link['title'])
            self._redirects = sorted(self._redirects)
        return self._redirects

    @property
    def backlinks(self):
        ''' Pages that link to this page

        :getter: Returns the list of all pages that link to this page
        :setter: Not settable
        :type: list
        '''
        if not getattr(self, '_backlinks', False):
            self._backlinks = list()
            params = {
                'action': 'query',
                'list': 'backlinks',
                'bltitle': self.title,
                'bllimit': 'max',
                'blfilterredir': 'nonredirects',
                'blnamespace': 0
                }
            for link in self._continued_query(params, 'backlinks'):
                self._backlinks.append(link['title'])
            self._backlinks = sorted(self._backlinks)
        return self._backlinks

    @property
    def summary(self):
        ''' Default page summary

        :getter: Returns the first section of the MediaWiki page
        :setter: Not settable
        :type: string
        '''
        if not getattr(self, '_summary', False):
            self._summary = self.summarize()
        return self._summary

    def summarize(self, sentences=0, chars=0):
        ''' Summarize page either by number of sentences, chars, or first
        section (**default**)

        :param sentences: Number of sentences to use in summary \
        (first `x` sentences)
        :type sentences: integer
        :param chars: Number of characters to use in summary \
        (first `x` characters)
        :type chars: integer
        :returns: string

        .. note:: Precedence for parameters: sentences then chars; \
        if both are 0 then the entire first section is returned
        '''
        query_params = {
            'prop': 'extracts',
            'explaintext': '',
            'titles': self.title
        }
        if sentences:
            query_params['exsentences'] = (10 if sentences > 10 else sentences)
        elif chars:
            query_params['exchars'] = (1 if chars < 1 else chars)
        else:
            query_params['exintro'] = ''

        request = self.mediawiki.wiki_request(query_params)
        summary = request['query']['pages'][self.pageid]['extract']
        return summary

    @property
    def sections(self):
        ''' Table of contents sections

        :getter: Returns the sections listed in the table of contents
        :setter: Not settable
        :type: list
        '''
        if not getattr(self, '_sections', False):
            query_params = {'action': 'parse', 'prop': 'sections'}
            if not getattr(self, 'title', None):
                query_params['pageid'] = self.pageid
            else:
                query_params['page'] = self.title
            request = self.mediawiki.wiki_request(query_params)
            sections = request['parse']['sections']
            self._sections = [section['line'] for section in sections]

        return self._sections

    def section(self, section_title):
        ''' Plain text section content

        :param section_title: Name of the section to pull
        :type section_title: string
        :returns: string or None if section title is not found

        .. note:: Returns **None** if section title is not found; \
        only text between title and next section or sub-section title \
        is returned.
        '''
        section = u'== {0} =='.format(section_title)
        try:
            index = self.content.index(section) + len(section)
        except ValueError:
            return None

        try:
            next_index = self.content.index('==', index)
        except ValueError:
            next_index = len(self.content)

        return self.content[index:next_index].lstrip('=').strip()

    # Protected Methods
    def __load(self, redirect=True, preload=False):
        ''' load the basic page information '''
        query_params = {
            'prop': 'info|pageprops',
            'inprop': 'url',
            'ppprop': 'disambiguation',
            'redirects': '',
        }
        query_params.update(self.__title_query_param())

        request = self.mediawiki.wiki_request(query_params)

        query = request['query']
        pageid = list(query['pages'].keys())[0]
        page = query['pages'][pageid]

        # determine result of the request
        # missing is present if the page is missing
        if 'missing' in page:
            self._raise_page_error()
        # redirects is present in query if page is a redirect
        elif 'redirects' in query:
            self._handle_redirect(redirect, preload, query, page)
        # if pageprops is returned, it must be a disambiguation error
        elif 'pageprops' in page:
            self._raise_disambiguation_error(page, pageid)
        else:
            self.pageid = pageid
            self.title = page['title']
            self.url = page['fullurl']
    # end __load

    def _raise_page_error(self):
        ''' raise the correct type of page error '''
        if hasattr(self, 'title'):
            raise PageError(title=self.title)
        else:
            raise PageError(pageid=self.pageid)

    def _raise_disambiguation_error(self, page, pageid):
        ''' parse and throw a disambiguation error '''
        query_params = {
            'prop': 'revisions',
            'rvprop': 'content',
            'rvparse': '',
            'rvlimit': 1
        }
        query_params.update(self.__title_query_param())
        request = self.mediawiki.wiki_request(query_params)
        html = request['query']['pages'][pageid]['revisions'][0]['*']

        lis = BeautifulSoup(html, 'html.parser').find_all('li')
        filtered_lis = [li for li in lis if 'tocsection' not in
                        ''.join(li.get('class', list()))]
        may_refer_to = [li.a.get_text()
                        for li in filtered_lis if li.a]
        disambiguation = list()
        for lis_item in filtered_lis:
            item = lis_item.find_all('a')[0]
            if item:
                one_disambiguation = dict()
                one_disambiguation['title'] = item['title']
                one_disambiguation['description'] = lis_item.text
                disambiguation.append(one_disambiguation)
        raise DisambiguationError(getattr(self, 'title', page['title']),
                                  may_refer_to,
                                  disambiguation)

    def _handle_redirect(self, redirect, preload, query, page):
        ''' handle redirect '''
        if redirect:
            redirects = query['redirects'][0]

            if 'normalized' in query:
                normalized = query['normalized'][0]
                if normalized['from'] != self.title:
                    raise MediaWikiException(ODD_ERROR_MESSAGE)
                # assert normalized['from'] == self.title, ODD_ERROR_MESSAGE
                from_title = normalized['to']
            else:
                if not getattr(self, 'title', None):
                    self.title = redirects['from']
                    delattr(self, 'pageid')
                from_title = self.title
            if redirects['from'] != from_title:
                raise MediaWikiException(ODD_ERROR_MESSAGE)
            # assert redirects['from'] == from_title, ODD_ERROR_MESSAGE

            # change the title and reload the whole object
            self.__init__(self.mediawiki, title=redirects['to'],
                          redirect=redirect, preload=preload)
        else:
            raise RedirectError(getattr(self, 'title', page['title']))

    def _continued_query(self, query_params, key='pages'):
        '''
        Based on https://www.mediawiki.org/wiki/API:Query#Continuing_queries
        '''
        query_params.update(self.__title_query_param())

        last_continue = dict()
        prop = query_params.get('prop')

        while True:
            params = query_params.copy()
            params.update(last_continue)

            request = self.mediawiki.wiki_request(params)

            if 'query' not in request:
                break

            pages = request['query'][key]
            if 'generator' in query_params:
                for datum in pages.values():
                    yield datum
            elif isinstance(pages, list):
                for datum in list(enumerate(pages)):
                    yield datum[1]
            else:
                for datum in pages[self.pageid].get(prop, list()):
                    yield datum

            if 'continue' not in request:
                break

            last_continue = request['continue']
    # end _continued_query

    def __title_query_param(self):
        ''' util function to determine which parameter method to use '''
        if getattr(self, 'title', None) is not None:
            return {'titles': self.title}
        else:
            return {'pageids': self.pageid}
    # end __title_query_param

# end MediaWikiPage Class
