'''
MediaWiki class module
'''
# MIT License
# Author: Tyler Barrus (barrust@gmail.com)

from __future__ import (unicode_literals, absolute_import)
from datetime import (datetime, timedelta)
import time
from decimal import (Decimal, DecimalException)
import requests
from .exceptions import (MediaWikiException, PageError, MediaWikiAPIURLError,
                         HTTPTimeoutError, MediaWikiGeoCoordError,
                         MediaWikiCategoryTreeError)
from .mediawikipage import (MediaWikiPage)
from .utilities import (memoize)

URL = 'https://github.com/barrust/mediawiki'
VERSION = '0.3.15'


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

    def __init__(self, url='http://{lang}.wikipedia.org/w/api.php', lang='en',
                 timeout=None, rate_limit=False,
                 rate_limit_wait=timedelta(milliseconds=50)):
        ''' Init Function '''
        self._version = VERSION
        self._lang = lang.lower()
        self._api_url = url.format(lang=self._lang)
        self._timeout = timeout
        self._user_agent = ('python-mediawiki/VERSION-{0}'
                            '/({1})/BOT').format(VERSION, URL)
        self._session = None
        self._rate_limit = rate_limit
        self._rate_limit_last_call = None
        self._min_wait = rate_limit_wait
        self._extensions = None
        self._api_version = None
        self._base_url = None
        self.__supported_languages = None

        # for memoized results
        self._cache = dict()
        self._refresh_interval = None

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
    def base_url(self):
        ''' Base URL for the MediaWiki site

        :getter: Returns the base url of the site
        :setter: Not settable
        :type: string
        '''
        return self._base_url

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

    @property
    def refresh_interval(self):
        ''' The interval at which the memoize cache is to be refresh

        :getter: Returns the refresh interval for the memoize cache
        :setter: Sets the refresh interval for the memoize cache
        :return: integer
        '''
        return self._refresh_interval

    @refresh_interval.setter
    def refresh_interval(self, refresh_interval):
        ''' Set the new cache refresh interval '''
        if isinstance(refresh_interval, int) and refresh_interval > 0:
            self._refresh_interval = refresh_interval
        else:
            self._refresh_interval = None

    # non-properties
    def set_api_url(self, api_url='http://{lang}.wikipedia.org/w/api.php',
                    lang='en'):
        ''' Set the API URL and language

        :param api_url: API URL to use
        :type pages: string
        :param lang: Language of the API URL
        :type pages: string

        :raises `mediawiki.exceptions.MediaWikiAPIURLError`: \
        if the url is not a valid MediaWiki site
        '''
        old_api_url = self._api_url
        old_lang = self._lang
        self._lang = lang.lower()
        self._api_url = api_url.format(lang=self._lang)
        try:
            self._get_site_info()
            self.__supported_languages = None  # reset this
        except Exception:
            # reset api url and lang in the event that the exception was caught
            self._api_url = old_api_url
            self._lang = old_lang
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
    @property
    def supported_languages(self):
        ''' All supported language prefixes on the MediaWiki site

        :getter: Returns all supported language prefixes
        :setter: Not settable
        :returns: dict: prefix - local language name pairs
        '''
        if self.__supported_languages is None:
            res = self.wiki_request({'meta': 'siteinfo', 'siprop':
                                     'languages'})
            tmp = res['query']['languages']
            supported = {lang['code']: lang['*'] for lang in tmp}
            self.__supported_languages = supported
        return self.__supported_languages

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
            sug = None
            if raw_results['query'].get('searchinfo'):
                sug = raw_results['query']['searchinfo']['suggestion']
            return list(search_results), sug

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
        :returns: Either a tuple ([pages], [subcategories]) or just the \
        list of pages

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
        last_cont = dict()
        while not finished:
            params = search_params.copy()
            params.update(last_cont)
            raw_res = self.wiki_request(params)

            self._check_error_response(raw_res, category)

            current_pull = len(raw_res['query']['categorymembers'])
            for rec in raw_res['query']['categorymembers']:
                if rec['type'] == 'page':
                    pages.append(rec['title'])
                elif rec['type'] == 'subcat':
                    tmp = rec['title']
                    if tmp.startswith('Category:'):
                        tmp = tmp[9:]
                    subcats.append(tmp)

            if 'continue' not in raw_res or last_cont == raw_res['continue']:
                break

            returned_results = returned_results + current_pull
            if results is None or (results - returned_results > 0):
                last_cont = raw_res['continue']
            else:
                finished = True
        # end while loop

        if subcategories:
            return pages, subcats
        return pages
    # end categorymembers

    def categorytree(self, category, depth=5):
        ''' Generate the Category Tree for the given categories

        :param category: Category name
        :type category: string or list of strings
        :param depth: Depth to traverse the tree
        :type depth: integer or None
        :returns: Dictionary of the category tree structure
        :rtype: Dictionary
        :Return Data Structure: Subcategory contains the same recursive \
        structure

        >>> {
                'category': {
                    'depth': Number,
                    'links': list,
                    'parent-categories': list,
                    'sub-categories': dict
                }
            }

        .. versionadded:: 0.3.10

        .. note:: Set depth to **None** to get the whole tree
        '''
        def __cat_tree_rec(cat, depth, tree, level, categories, links):
            ''' recursive function to build out the tree '''
            tree[cat] = dict()
            tree[cat]['depth'] = level
            tree[cat]['sub-categories'] = dict()
            tree[cat]['links'] = list()
            tree[cat]['parent-categories'] = list()
            parent_cats = list()

            if cat not in categories:
                tries = 0
                while True:
                    if tries > 10:
                        raise MediaWikiCategoryTreeError(cat)
                    try:
                        categories[cat] = self.page('Category:{0}'.format(cat))
                        parent_cats = categories[cat].categories
                        links[cat] = self.categorymembers(cat, results=None,
                                                          subcategories=True)
                        break
                    except PageError:
                        raise PageError('Category:{0}'.format(cat))
                    except Exception:
                        tries = tries + 1
                        time.sleep(1)
            else:
                parent_cats = categories[cat].categories

            for pcat in parent_cats:
                tree[cat]['parent-categories'].append(pcat)

            for link in links[cat][0]:
                tree[cat]['links'].append(link)

            if depth and level >= depth:
                for ctg in links[cat][1]:
                    tree[cat]['sub-categories'][ctg] = None
            else:
                for ctg in links[cat][1]:
                    __cat_tree_rec(ctg, depth,
                                   tree[cat]['sub-categories'], level + 1,
                                   categories, links)
            return
        # end __cat_tree_rec

        # ###################################
        # ### Actual Function Code        ###
        # ###################################

        # make it simple to use both a list or a single category term
        if not isinstance(category, list):
            cats = [category]
        else:
            cats = category

        # parameter verification
        if len(cats) == 1 and (cats[0] is None or cats[0] == ''):
            msg = ("CategoryTree: Parameter 'category' must either "
                   "be a list of one or more categories or a string; "
                   "provided: '{}'".format(category))
            raise ValueError(msg)

        if depth is not None and depth < 1:
            msg = ("CategoryTree: Parameter 'depth' must None (for the full "
                   "tree) be greater than 0")
            raise ValueError(msg)

        results = dict()
        categories = dict()
        links = dict()

        for cat in cats:
            if cat is None or cat == '':
                continue
            __cat_tree_rec(cat, depth, results, 0, categories, links)
        return results
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

        :raises  ValueError: when title is blank or None and no pageid is \
        provided
        :raises  `mediawiki.exceptions.PageError`: if page does not exist

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
        ''' Parse out the Wikimedia site information including
        API Version and Extensions '''
        response = self.wiki_request({
            'meta': 'siteinfo',
            'siprop': 'extensions|general'
        })

        # shouldn't a check for success be done here?
        gen = response['query']['general']
        api_version = gen['generator'].split(' ')[1].split('-')[0]

        major_minor = api_version.split('.')
        for i, item in enumerate(major_minor):
            major_minor[i] = int(item)
        self._api_version = tuple(major_minor)

        # parse the base url out
        tmp = gen['server']
        if tmp.startswith('http://') or tmp.startswith('https://'):
            self._base_url = tmp
        elif gen['base'].startswith('https:'):
            self._base_url = 'https:{}'.format(tmp)
        else:
            self._base_url = 'http:{}'.format(tmp)

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
