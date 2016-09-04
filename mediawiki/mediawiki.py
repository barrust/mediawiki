'''
MediaWiki class module
'''
# MIT License
# Author: Tyler Barrus (barrust@gmail.com)

from __future__ import unicode_literals
import requests
import sys
import time
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
        self._version = '0.0.1-prealpha'
        self._api_url = url
        self._lang = lang
        self._timeout = timeout
        self._user_agent = ('python-mediawiki/VERSION-{0}'
                            '/(https://github.com/barrust/mediawiki/)'
                            '/BOT'.format(self._version))
        self._session = None
        self._rate_limit = rate_limit
        self._rate_limit_last_call = None
        self._min_wait = rate_limit_wait
        self._extensions = None
        self._api_version = None

        # call helper functions to get everything set up
        self.reset_session()
        self._get_site_info()

    # non-settable properties
    @property
    def version(self):
        ''' Get current version of the library '''
        return self._version

    @property
    def api_version(self):
        ''' get site's api version '''
        return '.'.join([str(x) for x in self._api_version])

    @property
    def extensions(self):
        ''' get site's installed extensions '''
        return self._extensions

    # settable properties
    @property
    def rate_limit(self):
        ''' get if using rate limiting '''
        return self._rate_limit

    @rate_limit.setter
    def rate_limit(self, rate_limit):
        ''' set rate limiting of api usage '''
        self._rate_limit = bool(rate_limit)
        self._rate_limit_last_call = None
        # TODO: add cache to project and clear it here

    @property
    def rate_limit_min_wait(self):
        ''' get minimum wait for rate limiting '''
        return self._min_wait

    @rate_limit_min_wait.setter
    def rate_limit_min_wait(self, min_wait):
        ''' set minimum wait for rate limiting '''
        self._min_wait = min_wait
        self._rate_limit_last_call = None

    @property
    def timeout(self):
        ''' get timeout setting; None means no timeout '''
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        '''
        set request timeout in seconds (or fractions of a second)
        None means no timeout
        '''
        self._timeout = timeout

    @property
    def language(self):
        ''' return current language '''
        return self._lang

    @language.setter
    def language(self, lang):
        '''
        set the language of the url

        Note: use correct language titles with the updated url
        '''
        lang = lang.lower()
        if self._lang == lang:
            return

        url = self._api_url
        tmp = url.replace('/{0}.'.format(self._lang), '/{0}.'.format(lang))

        self._api_url = tmp
        self._lang = lang
        # TODO: add cache to project and clear it here

    @property
    def user_agent(self):
        ''' get user_agent '''
        return self._user_agent

    @user_agent.setter
    def set_user_agent(self, user_agent):
        ''' set a new user agent '''
        self._user_agent = user_agent
        self.reset_session()

    @property
    def api_url(self):
        ''' get url to the api '''
        return self._api_url

    # non-properties
    def set_api_url(self, api_url='http://en.wikipedia.org/w/api.php',
                    lang='en'):
        ''' set the url to the api '''
        self._api_url = api_url
        self._lang = lang
        try:
            self._get_site_info()
        except Exception:
            raise MediaWikiAPIURLError(api_url)
        # TODO: add cache to project and clear it here

    def reset_session(self):
        ''' Set session information '''
        headers = {'User-Agent': self._user_agent}
        self._session = requests.Session()
        self._session.headers.update(headers)

    # non-setup functions
    def languages(self):
        '''
        List all the currently supported language prefixes (usually ISO
        language code). Result is a <prefix>: <local_lang_name> pairs
        dictionary.
        '''
        res = self._wiki_request({'meta': 'siteinfo', 'siprop': 'languages'})
        return {lang['code']: lang['*'] for lang in res['query']['languages']}
    # end languages

    def random(self, pages=1):
        ''' return a random page title or list of titles '''
        if pages is None or pages < 1:
            raise ValueError('Number of pages must be greater than 0')

        query_params = {'list': 'random', 'rnnamespace': 0, 'rnlimit': pages}

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

    def categorymembers(self, category, results=10, subcategories=True):
        ''' get informaton about a category '''
        if category is None or category.strip() == '':
            raise ValueError("Category must be specified")

        search_params = {
            'list': 'categorymembers',
            'cmprop': 'ids|title|type',
            'cmtype': ('page|subcat' if subcategories else 'page'),
            'cmlimit': results,
            'cmtitle': 'Category:{0}'.format(category)
        }

        raw_results = self._wiki_request(search_params)

        self._check_error_response(raw_results, category)

        pages = list()
        subcats = list()
        for rec in raw_results['query']['categorymembers']:
            if rec['type'] == 'page':
                pages.append(rec['title'])
            elif rec['type'] == 'subcat':
                tmp = rec['title']
                if tmp.startswith('Category:'):
                    tmp = tmp[9:]
                subcats.append(tmp)
        if subcategories:
            return pages, subcats
        else:
            return pages
    # end categorymembers

    def categorytree(self, category, depth=5):
        raise NotImplementedError

    def page(self, title=None, pageid=None, auto_suggest=True, redirect=True,
             preload=False):
        if (title is None or title.strip() == '') and pageid is None:
            raise ValueError("Title or Pageid must be specified")
        elif title:
            if auto_suggest:
                res, suggest = self.search(title, results=1, suggestion=True)
                try:
                    title = suggest or res[0]
                except IndexError:
                    # page doesn't exist if no suggestion or search results
                    raise PageError(title=title)
            return MediaWikiPage(self, title, redirect=redirect,
                                 preload=preload)
        else:  # must be pageid
            return MediaWikiPage(self, pageid=pageid, preload=preload)
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

        limit = self._rate_limit
        last_call = self._rate_limit_last_call
        if limit and last_call and last_call + self._min_wait > datetime.now():
            # call time to quick for rate limited api requests, wait
            wait_time = (last_call + self._min_wait) - datetime.now()
            time.sleep(int(wait_time.total_seconds()))

        if self._session is None:
            self.reset_session()

        req = self._session.get(self._api_url, params=params,
                                timeout=self._timeout)

        if self._rate_limit:
            self._rate_limit_last_call = datetime.now()

        return req.json(encoding='utf-8')
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
        api_version = gen.split(" ")[1].split("-")[0]

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
        if 'error' in response:
            error_codes = ['HTTP request timed out.', 'Pool queue is full']
            if response['error']['info'] in error_codes:
                raise HTTPTimeoutError(query)
            else:
                raise MediaWikiException(response['error']['info'])
        else:
            return

# end MediaWiki class


# TODO: Should this be in it's own file?
class MediaWikiPage(object):
    '''
    Instance of a media wiki page

    Note: This should never need to be called directly by the user!
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
            raise ValueError("Either a title or a pageid must be specified")

        self.__load(redirect=redirect, preload=preload)

        if preload:
            for prop in ('content', 'summary', 'images', 'references', 'links',
                         'sections', 'redirects', 'coordinates', 'backlinks',
                         'categories'):
                try:
                    getattr(self, prop)
                except Exception:
                    pass
        # end __init__

    def __repr__(self):
        encoding = sys.stdout.encoding or 'utf-8'
        tmp = u'<WikipediaPage \'{0}\'>'.format(self.title)
        if sys.version_info > (3, 0):
            return tmp.encode(encoding).decode(encoding)
        return tmp.encode(encoding)

    def __eq__(self, other):
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
            request = self.mediawiki._wiki_request(query_params)
            page_info = request['query']['pages'][self.pageid]
            self._content = page_info['extract']
            self._revision_id = page_info['revisions'][0]['revid']
            self._parent_id = page_info['revisions'][0]['parentid']
        return self._content, self._revision_id, self._parent_id

    @property
    def content(self):
        ''' get content, revision_id and parent_id '''
        if not getattr(self, '_content', False):
            self._pull_content_revision_parent()
        return self._content

    @property
    def revision_id(self):
        ''' Get current revision id '''
        if not getattr(self, '_revision_id', False):
            self._pull_content_revision_parent()
        return self._revision_id

    @property
    def parent_id(self):
        ''' Get current revision id '''
        if not getattr(self, '_parent_id', False):
            self._pull_content_revision_parent()
        return self._parent_id

    @property
    def images(self):
        ''' List of URLs of images on the page '''
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

        return self._images

    @property
    def references(self):
        ''' List of URLs of external links on a page '''
        if not getattr(self, '_references', False):
            params = {'prop': 'extlinks', 'ellimit': 'max'}
            self._references = list()
            for link in self._continued_query(params):
                if link['*'].startswith('http'):
                    url = link['*']
                else:
                    url = 'http:{0}'.format(link['*'])
                self._references.append(url)

        return self._references

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

        request = self.mediawiki._wiki_request(query_params)

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
        raise DisambiguationError(getattr(self, 'title', page['title']),
                                  may_refer_to,
                                  disambiguation)

    def _handle_redirect(self, redirect, preload, query, page):
        ''' handle redirect '''
        if redirect:
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

            request = self.mediawiki._wiki_request(params)

            if 'query' not in request:
                break

            pages = request['query'][key]
            if 'generator' in query_params:
                for datum in pages.values():
                    yield datum
            else:
                print("yeilding:", query_params)  # just testing this
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
