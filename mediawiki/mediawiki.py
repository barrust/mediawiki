# -*- coding: utf-8 -*-

# MIT License
# Author: Tyler Barrus (barrust@gmail.com)

from __future__ import unicode_literals
import requests
import sys
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from .exceptions import (MediaWikiException, PageError,
                         RedirectError, DisambiguationError,
                         MediaWikiAPIURLError, HTTPTimeoutError,
                         ODD_ERROR_MESSAGE)


class MediaWiki(object):
    ''' Base MediaWiki object '''

    def __init__(self, url='http://en.wikipedia.org/w/api.php', lang='en',
                 timeout=None, rate_limit=False,
                 rate_limit_wait=timedelta(milliseconds=50)):
        self.api_url = url
        self.lang = lang
        self.timeout = timeout
        self.user_agent = ('python-mediawiki/VERSION-{0}'
                           '/(https://github.com/barrust/mediawiki/)'
                           '/BOT'.format(MediaWiki.get_version()))
        self.session = None
        self.rate_limit = rate_limit
        self.rate_limit_last_call = None
        self.min_wait = rate_limit_wait
        self.extensions = None
        self.api_version = None
        self.api_version_major_minor = None
        self.version = MediaWiki.get_version()

        # call helper functions to get everything set up
        self.reset_session()
        self._get_site_info()

    @classmethod
    def get_version(cls):
        ''' Get current version of the library '''
        return '0.0.1-prealpha'

    def reset_session(self):
        ''' Set session information '''
        headers = {'User-Agent': self.user_agent}
        self.session = requests.Session()
        self.session.headers.update(headers)

    def set_rate_limiting(self, rate_limit,
                          min_wait=timedelta(milliseconds=50)):
        ''' set rate limiting of api usage '''
        if not rate_limit:
            self.rate_limit = False
            self.min_wait = None
        else:
            self.rate_limit = True
            self.min_wait = min_wait
        self.rate_limit_last_call = None
        # TODO: add cache to project and clear it here

    def set_timeout(self, timeout):
        ''' set request timeout '''
        self.timeout = timeout

    def set_api_url(self, api_url='http://en.wikipedia.org/w/api.php',
                    lang='en'):
        ''' set the url to the api '''
        self.api_url = api_url
        self.lang = lang
        try:
            self._get_site_info()
        except Exception as e:
            raise MediaWikiAPIURLError(api_url)
        # TODO: add cache to project and clear it here

    def set_language(self, lang):
        '''
        set the language of the url

        Note: use correct language titles with the updated url
        '''
        if self.lang == lang:
            return
        tmp_url = self.api_url.replace('/{0}.'.format(self.lang),
                                       "/{0}.".format(lang.lower()))

        self.api_url = tmp_url
        self.lang = lang
        # TODO: add cache to project and clear it here

    def set_user_agent(self, user_agent):
        ''' set a new user agent '''
        self.user_agent = user_agent
        self.reset_session()

    # non-setup functions
    def languages(self):
        '''
        List all the currently supported language prefixes (usually ISO
        language code). Result is a <prefix>: <local_lang_name> pairs
        dictionary.
        '''
        response = self._wiki_request({
                'meta': 'siteinfo',
                'siprop': 'languages'
            })

        return {lang['code']: lang['*'] for
                lang in response['query']['languages']}
    # end languages

    def random(self, pages=1):
        ''' return a random page title or list of titles '''

        if pages is None or pages < 1:
            raise ValueError('Number of pages must be greater than 0')

        query_params = {
            'list': 'random',
            'rnnamespace': 0,
            'rnlimit': pages,
        }

        request = self._wiki_request(query_params)
        titles = [page['title'] for page in request['query']['random']]

        if len(titles) == 1:
            return titles[0]

        return titles
    # end random

    def search(self, query, results=10, suggestion=False):
        '''
        Conduct a search for "query" returning "results" results

        If suggestion is True, returns results and suggestions
        (if any) in a tuple
        '''
        if query is None or query.strip() == '':
            raise ValueError("Query must be specified")
        search_params = {
            'list': 'search',
            'srprop': '',
            'srlimit': results,
            'srsearch': query
        }
        if suggestion:
            search_params['srinfo'] = 'suggestion'

        raw_results = self._wiki_request(search_params)

        # this should be pushed to its own function
        if 'error' in raw_results:
            error_codes = ['HTTP request timed out.', 'Pool queue is full']
            if raw_results['error']['info'] in error_codes:
                raise HTTPTimeoutError(query)
            else:
                raise MediaWikiException(raw_results['error']['info'])

        search_results = (d['title'] for d in raw_results['query']['search'])

        if suggestion:
            if raw_results['query'].get('searchinfo'):
                sug = raw_results['query']['searchinfo']['suggestion']
                return list(search_results), sug
            else:
                return list(search_results), None

        return list(search_results)
    # end search

    def suggest(self, query):
        '''
        Gather suggestions based on the provided "query" or None if
        no suggestions found
        '''
        search_results = self.search(query, results=1, suggestion=True)
        return search_results[1]
    # end suggest

    def geosearch(self, latitude, longitude, title=None, results=10,
                  radius=1000):
        raise NotImplementedError

    def opensearch(self, query, results=10, redirect=False):
        raise NotImplementedError

    def prefexsearch(self, query, results=10):
        raise NotImplementedError

    def summary(self, title, sentences=0, chars=0, auto_suggest=True,
                redirect=True):
        raise NotImplementedError

    def categorymembers(self, category, results=10,
                        subcategories=True):
        raise NotImplementedError

    def categorytree(self, category, depth=5):
        raise NotImplementedError

    def page(self, title=None, pageid=None, auto_suggest=True,
             redirect=True, preload=False):
        if title is not None and title.strip() != '':
            if auto_suggest:
                results, suggestion = self.search(title, results=1,
                                                  suggestion=True)
                try:
                    # should these be flipped?
                    print("did i really get here?")
                    title = suggestion or results[0]
                except IndexError:
                    # if there is no suggestion or search results,
                    # the page doesn't exist
                    raise PageError(title)
            print(title)
            return MediaWikiPage(self, title, redirect=redirect,
                                 preload=preload)
        elif pageid is not None:
            return MediaWikiPage(self, pageid=pageid, preload=preload)
        else:
            raise ValueError(("Either a title or a pageid must be "
                              "specified"))
    # end page

    # Private functions
    # Not to be called from outside
    def _wiki_request(self, params):
        '''
        Make a request to the MediaWiki API using the given search
        parameters

        Returns a parsed dict of the JSON response
        '''

        params['format'] = 'json'
        if 'action' not in params:
            params['action'] = 'query'

        if (
            self.rate_limit and self.rate_limit_last_call and
            self.rate_limit_last_call + self.min_wait > datetime.now()
        ):
            # call time to quick for rate limited api requests, wait
            wait_time = (last_call + wait) - datetime.now()
            time.sleep(int(wait_time.total_seconds()))

        if self.session is None:
            reset_session()

        r = self.session.get(self.api_url, params=params, timeout=self.timeout)

        if self.rate_limit:
            self.rate_limit_last_call = datetime.now()

        return r.json(encoding='utf-8')
    # end _wiki_request

    def _get_site_info(self):
        '''
        Parse out the Wikimedia site information including
        API Version and Extensions
        '''
        response = self._wiki_request({
            'meta': 'siteinfo',
            'siprop': 'extensions|general'
        })

        gen = response['query']['general']['generator']
        self.api_version = gen.split(" ")[1].split("-")[0]

        major_minor = self.api_version.split('.')
        for i, item in enumerate(major_minor):
            major_minor[i] = int(item)
        self.api_version_major_minor = major_minor

        self.extensions = set()
        for ext in response['query']['extensions']:
            self.extensions.add(ext['name'])
    # end _get_site_info

# end MediaWiki class


class MediaWikiPage(object):
    '''
    Instance of a media wiki page

    Note: This should never need to be called directly by the user!
    '''

    def __init__(self, mediawiki, title=None, pageid=None,
                 redirect=True, preload=False, original_title=''):
        self.mediawiki = mediawiki

        if title is not None:
            self.title = title
            self.original_title = original_title or title
        elif pageid is not None:
            self.pageid = pageid
        else:
            raise ValueError("Either a title or a pageid must be specified")
        print(title)
        self.__load(redirect=redirect, preload=preload)

        # if preload:
        #     for prop in ('content', 'summary', 'images',
        #                  'references', 'links', 'sections',
        #                  'redirects', 'coordinates', 'backlinks',
        #                  'categories'):
        #         try:
        #             getattr(self, prop)
        #         except Exception:
        #             pass
        # end __init__

    def __repr__(self):
        encoding = sys.stdout.encoding or 'utf-8'
        u = u'<WikipediaPage \'{0}\'>'.format(self.title)
        if sys.version_info > (3, 0):
            return u.encode(encoding).decode(encoding)
        return u.encode(encoding)

    def __eq__(self, other):
        try:
            return (
                self.pageid == other.pageid and
                self.title == other.title and
                self.url == other.url
            )
        except AttributeError as ex:
            return False

    def __load(self, redirect=True, preload=False):
        ''' load the basic page information '''
        query_params = {
            'prop': 'info|pageprops',
            'inprop': 'url',
            'ppprop': 'disambiguation',
            'redirects': '',
        }
        query_params.update(self.__title_query_param)

        request = self.mediawiki._wiki_request(query_params)
        print(request)
        query = request['query']
        pageid = list(query['pages'].keys())[0]
        page = query['pages'][pageid]

        # determine result of the request
        # missing is present if the page is missing
        if 'missing' in page:
            if hasattr(self, 'title'):
                raise PageError(self.title)
            else:
                raise PageError(pageid=self.pageid)
        # redirects is present in query if page is a redirect
        elif 'redirects' in query:
            print (" found redirects: {0}".format(redirect))
            if redirect:
                print("redirects")
                redirects = query['redirects'][0]

                if 'normalized' in query:
                    normalized = query['normalized'][0]
                    assert normalized['from'] == self.title, ODD_ERROR_MESSAGE
                    from_title = normalized['to']
                else:
                    if not getattr(self, 'title', None):
                        self.title = redirects['from']
                        delattr(self, 'pageid')
                    from_title = self.title
                assert redirects['from'] == from_title, ODD_ERROR_MESSAGE

                # change the title and reload the whole object
                self.__init__(self.mediawiki, title=redirects['to'],
                              redirect=redirect, preload=preload)
            else:
                print('huh...')
                raise RedirectError(getattr(self, 'title', page['title']))
        # if pageprops is returned, it must be a disambiguation error
        elif 'pageprops' in page:
            query_params = {
                'prop': 'revisions',
                'rvprop': 'content',
                'rvparse': '',
                'rvlimit': 1
            }
            query_params.update(self.__title_query_param)
            request = self.mediawiki._wiki_request(query_params)
            html = request['query']['pages'][pageid]['revisions'][0]['*']

            lis = BeautifulSoup(html, 'html.parser').find_all('li')
            filtered_lis = [li for li in lis if 'tocsection' not in
                            ''.join(li.get('class', list()))]
            may_refer_to = [li.a.get_text()
                            for li in filtered_lis if li.a]
            disambiguation = list()
            for lis_item in filtered_lis:
                item = lis_item.find_all("a")[0]
                if item:
                    one_disambiguation = dict()
                    one_disambiguation["title"] = item["title"]
                    one_disambiguation["description"] = lis_item.text
                    disambiguation.append(one_disambiguation)
            raise DisambiguationError(getattr(self, 'title',
                                      page['title']), may_refer_to,
                                      disambiguation)
        else:
            self.pageid = pageid
            self.title = page['title']
            self.url = page['fullurl']
    # end __load

    def __continued_query(self, query_params, key='pages'):
        '''
        Based on https://www.mediawiki.org/wiki/API:Query#Continuing_queries
        '''
        query_params.update(self.__title_query_param)

        last_continue = dict()
        prop = query_params.get('prop')

        while True:
            params = query_params.copy()
            params.update(last_continue)

            request = self._wiki_request(params)

            if 'query' not in request:
                break

            pages = request['query'][key]
            if 'generator' in query_params:
                for datum in pages.values():
                    yield datum
            else:
                print(query_params)  # just testing this
                for datum in pages[self.pageid].get(prop, list()):
                    yield datum

            if 'continue' not in request:
                break

            last_continue = request['continue']
    # end __continued_query

    @property
    def __title_query_param(self):
        ''' util function to determine which parameter method to use '''
        if getattr(self, 'title', None) is not None:
            return {'titles': self.title}
        else:
            return {'pageids': self.pageid}
    # end __title_query_param

# end MediaWikiPage Class
