'''
Unittest class
'''
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)
from mediawiki import (MediaWiki, PageError, RedirectError,
                       DisambiguationError, MediaWikiAPIURLError,
                       MediaWikiGeoCoordError, HTTPTimeoutError,
                       MediaWikiException)
import mediawiki
import unittest
import json
from datetime import timedelta
from decimal import Decimal


class MediaWikiOverloaded(MediaWiki):
    ''' Overload the MediaWiki class to change how wiki_request works '''
    def __init__(self, url='http://en.wikipedia.org/w/api.php', lang='en',
                 timeout=None, rate_limit=False,
                 rate_limit_wait=timedelta(milliseconds=50)):
        ''' new init '''

        with open('./tests/mock_requests.json', 'r') as file_handle:
            self.requests = json.load(file_handle)
        with open('./tests/mock_responses.json', 'r') as file_handle:
            self.responses = json.load(file_handle)
        MediaWiki.__init__(self, url=url, lang=lang, timeout=timeout,
                           rate_limit=rate_limit,
                           rate_limit_wait=rate_limit_wait)

    def _get_response(self, params):
        ''' override the __get_response method '''
        new_params = json.dumps(tuple(sorted(params.items())))
        return self.requests[self.api_url][new_params]


class TestMediaWiki(unittest.TestCase):
    ''' Test the MediaWiki Class Basic functionality '''
    def test_version(self):
        ''' test version information '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.version, mediawiki.__version__)

    def test_api_url(self):
        ''' test the original api '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.api_url, 'http://en.wikipedia.org/w/api.php')

    def test_api_url_set(self):
        ''' test the api url being set at creation time '''
        site = MediaWikiOverloaded(url='http://awoiaf.westeros.org/api.php')
        response = site.responses[site.api_url]
        self.assertEqual(site.api_url, 'http://awoiaf.westeros.org/api.php')
        self.assertEqual(site.api_version, response['api_version'])
        self.assertEqual(site.extensions, response['extensions'])

    def test_change_lang(self):
        ''' test changing the language '''
        site = MediaWikiOverloaded()
        site.language = 'FR'
        self.assertEqual(site.language, 'fr')
        self.assertEqual(site.api_url, 'http://fr.wikipedia.org/w/api.php')

    def test_change_lang_same(self):
        ''' test changing the language to the same lang '''
        site = MediaWikiOverloaded(url='http://fr.wikipedia.org/w/api.php',
                                   lang='fr')
        site.language = 'FR'
        self.assertEqual(site.language, 'fr')
        self.assertEqual(site.api_url, 'http://fr.wikipedia.org/w/api.php')

    def test_change_lang_no_change(self):
        ''' test changing the language when url will not change '''
        site = MediaWikiOverloaded(url='http://awoiaf.westeros.org/api.php')
        site.language = 'FR'
        self.assertEqual(site.language, 'fr')
        self.assertEqual(site.api_url, 'http://awoiaf.westeros.org/api.php')

    def test_api_version(self):
        ''' test api version parsed correctly'''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.api_version, response['api_version'])

    def test_extensions(self):
        ''' test parsing extensions correctly '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.extensions, response['extensions'])

    def test_change_api_url(self):
        ''' test switching the api url '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.api_url, 'http://en.wikipedia.org/w/api.php')
        self.assertEqual(site.api_version, response['api_version'])
        self.assertEqual(site.extensions, response['extensions'])

        site.set_api_url('http://awoiaf.westeros.org/api.php', lang='en')
        response = site.responses[site.api_url]
        self.assertEqual(site.api_url, 'http://awoiaf.westeros.org/api.php')
        self.assertEqual(site.api_version, response['api_version'])
        self.assertEqual(site.extensions, response['extensions'])

    def test_change_user_agent(self):
        ''' test changing the user agent '''
        site = MediaWikiOverloaded()
        site.user_agent = 'test-user-agent'
        self.assertEqual(site.user_agent, 'test-user-agent')

    def test_languages(self):
        ''' test pulling wikimedia supported languages '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.languages(), response['languages'])

    def test_rate_limit(self):
        ''' test setting rate limiting '''
        site = MediaWikiOverloaded()
        site.rate_limit = True
        self.assertEqual(site.rate_limit, True)
        self.assertEqual(site._rate_limit_last_call, None)
        self.assertEqual(site.rate_limit_min_wait, timedelta(milliseconds=50))

    def test_rate_limit_min_wait(self):
        ''' test setting rate limiting min wait '''
        site = MediaWikiOverloaded()
        site.rate_limit_min_wait = timedelta(milliseconds=150)
        self.assertEqual(site.rate_limit, False)
        self.assertEqual(site._rate_limit_last_call, None)
        self.assertEqual(site.rate_limit_min_wait, timedelta(milliseconds=150))

    def test_rate_limit_min_wait_reset(self):
        ''' test setting rate limiting '''
        site = MediaWikiOverloaded(rate_limit=True)
        self.assertNotEqual(site._rate_limit_last_call, None)  # should be set
        site.rate_limit_min_wait = timedelta(milliseconds=150)
        self.assertEqual(site._rate_limit_last_call, None)
        self.assertEqual(site.rate_limit, True)
        self.assertEqual(site.rate_limit_min_wait, timedelta(milliseconds=150))

    def test_default_timeout(self):
        ''' set default timeout '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.timeout, None)

    def test_set_timeout(self):
        ''' test setting timeout '''
        site = MediaWikiOverloaded()
        site.timeout = 30
        self.assertEqual(site.timeout, 30)

    def test_memoized(self):
        ''' test returning the memoized cache '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.memoized, dict())

    def test_memoized_not_empty(self):
        ''' test returning the memoized cache; not empty '''
        site = MediaWikiOverloaded()
        site.search('chest set')
        self.assertNotEqual(site.memoized, dict())

    def test_clear_memoized(self):
        ''' test clearing the memoized cache '''
        site = MediaWikiOverloaded()
        site.search('chest set')
        self.assertNotEqual(site.memoized, dict())
        site.clear_memoized()
        self.assertEqual(site.memoized, dict())


class TestMediaWikiRandom(unittest.TestCase):
    ''' Test Random Functionality '''
    def test_random(self):
        ''' test pulling random pages '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.random(pages=1), response['random_1'])

    def test_random_2(self):
        ''' test pulling random pages '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.random(pages=2), response['random_2'])

    def test_random_10(self):
        ''' test pulling random pages '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.random(pages=10), response['random_10'])

    def test_random_202(self):
        ''' test pulling 202 random pages '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.random(pages=202), response['random_202'])
        msg = ("\nNOTE: This is supposed to be limited to 20 by the API, per "
               "the documentation, but it isn't...")
        print(msg)
        self.assertEqual(len(response['random_202']), 202)  # limit to 20

    def test_random_value_err_msg(self):
        ''' test that ValueError message thrown from random'''
        site = MediaWikiOverloaded()
        try:
            site.random(pages=None)
        except ValueError as ex:
            msg = 'Number of pages must be greater than 0'
            self.assertEqual(str(ex), msg)

    def test_random_value_err(self):
        ''' test that ValueError is thrown from random'''
        site = MediaWikiOverloaded()
        self.assertRaises(ValueError, lambda: site.random(pages=None))


class TestMediaWikiSearch(unittest.TestCase):
    ''' Test MediaWiki Page Search Functionality '''
    def test_search_no_sug(self):
        ''' test searching without suggestion '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        # test that default is suggestion False
        api_url = response['search_without_suggestion']
        sws = response['search_without_suggestion']
        self.assertEqual(site.search('chest set'), api_url)
        self.assertEqual(site.search('chest set', suggestion=False), sws)

    def test_search_sug_found(self):
        ''' test searching with suggestion where found '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        sws = response['search_with_suggestion_found']
        self.assertEqual(list(site.search('chest set', suggestion=True)), sws)

    def test_search_sug_not_found(self):
        ''' test searching with suggestion where not found '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        ssnf = response['search_with_suggestion_not_found']
        self.assertEqual(list(site.search('chess set', suggestion=True)), ssnf)

    def test_search_sug_not_found_sm(self):
        ''' test searching with small result limit test '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(
                         site.search('chess set', results=3,
                                     suggestion=False),
                         response['search_with_suggestion_not_found_small'])
        num_res = len(response['search_with_suggestion_not_found_small'])
        self.assertEqual(num_res, 3)  # limit to 500

    def test_search_sug_not_found_lg(self):
        '''
        test searching with suggestion where not found but limited to the
        correct number
        '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(
                         site.search('chess set', results=505,
                                     suggestion=False),
                         response['search_with_suggestion_not_found_large'])
        num_res = len(response['search_with_suggestion_not_found_large'])
        self.assertEqual(num_res, 500)  # limit to 500


class TestMediaWikiSuggest(unittest.TestCase):
    ''' test the suggest functionality '''
    def test_suggest(self):
        ''' test suggest fixes capitalization '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.suggest('new york'), 'New York')

    def test_suggest_yonkers(self):
        ''' test suggest finds page '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.suggest('yonkers'), 'Yonkers, New York')

    def test_suggest_no_results(self):
        ''' test suggest finds no results '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.suggest('gobbilygook'), None)


class TestMediaWikiGeoSearch(unittest.TestCase):
    ''' Test GeoSearch Functionality '''
    def test_geosearch_decimals(self):
        ''' test geosearch with Decimals lat / long '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.geosearch(latitude=Decimal('0.0'),
                                        longitude=Decimal('0.0')),
                         response['geosearch_decimals'])

    def test_geosearch_mix_types(self):
        ''' test geosearch with mix type lat / long '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.geosearch(latitude=Decimal('0.0'),
                                        longitude='0.0'),
                         response['geosearch_mix_types'])

    def test_geo_page_inv_lat_long(self):
        ''' test geosearch using page with invalid lat / long '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.geosearch(title='new york',
                                        latitude=Decimal('-9999999999.999'),
                                        longitude=Decimal('0.0'), results=22,
                                        radius=10000),
                         response['geosearch_page_invalid_lat_long'])

    def test_geo_page_rad_res_set(self):
        ''' test geosearch with radius and result set '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.geosearch(title='new york', results=22, radius=10000)
        self.assertEqual(res, response['geosearch_page_radius_results_set'])
        self.assertEqual(len(res), 22)

    def test_geo_page_rad_res(self):
        ''' test geosearch with radius set '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.geosearch(title='new york', radius=10000)
        self.assertEqual(res, response['geosearch_page_radius_results'])
        self.assertEqual(len(res), 10)

    def test_geo_page(self):
        ''' test geosearch using just page '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.geosearch(title='new york')
        self.assertEqual(res, response['geosearch_page'])
        self.assertEqual(len(res), 1)


class TestMediaWikiOpenSearch(unittest.TestCase):
    ''' Test OpenSearch Functionality '''
    def test_opensearch(self):
        ''' test opensearch with default values '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.opensearch('new york')
        for i, item in enumerate(res):
            res[i] = list(item)
        self.assertEqual(res, response['opensearch_new_york'])
        self.assertEqual(len(res), 10)

    def test_opensearch_result(self):
        ''' test opensearch with result set '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.opensearch('new york', results=5)
        for i, item in enumerate(res):
            res[i] = list(item)
        self.assertEqual(res, response['opensearch_new_york_result'])
        self.assertEqual(len(res), 5)

    def test_opensearch_redirect(self):
        ''' test opensearch with redirect set '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.opensearch('new york', redirect=False)
        for i, item in enumerate(res):
            res[i] = list(item)
        self.assertEqual(res, response['opensearch_new_york_redirect'])
        self.assertEqual(len(res), 10)

    def test_opensearch_res_red_set(self):
        ''' test opensearch with result and redirect set '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.opensearch('new york', results=5, redirect=False)
        for i, item in enumerate(res):
            res[i] = list(item)
        self.assertEqual(res, response['opensearch_new_york_result_redirect'])
        self.assertEqual(len(res), 5)


class TestMediaWikiPrefixSearch(unittest.TestCase):
    ''' Test PrefixSearch Functionality '''
    def test_prefix_search(self):
        ''' test basic prefix search '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.prefixsearch('ar')
        self.assertEqual(res, response['prefixsearch_ar'])
        self.assertEqual(len(res), 10)

    def test_prefix_search_ba(self):
        ''' test prefix search results 10 '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.prefixsearch('ba', results=10)
        self.assertEqual(res, response['prefixsearch_ba'])
        self.assertEqual(len(res), 10)

    def test_prefix_search_5(self):
        ''' test prefix search results 5 '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.prefixsearch('ba', results=5)
        self.assertEqual(res, response['prefixsearch_ba_5'])
        self.assertEqual(len(res), 5)

    def test_prefix_search_30(self):
        ''' test prefix search results 30 '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.prefixsearch('ba', results=30)
        self.assertEqual(res, response['prefixsearch_ba_30'])
        self.assertEqual(len(res), 30)


# class TestMediaWikiSummary(unittest.TestCase):


# class TestMediaWikiCategoryTree(unittest.TestCase):


class TestMediaWikiCategoryMembers(unittest.TestCase):
    ''' Test CategoryMember Functionality '''
    def test_cat_mems_with_subcats(self):
        ''' test categorymember with subcategories '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['category_members_with_subcategories']
        ctm = site.categorymembers('Chess', results=15, subcategories=True)
        self.assertEqual(list(ctm), res)  # list since json doesn't keep tuple

    def test_cat_mems_subcat_default(self):
        ''' test categorymember with default subcategories (True) '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['category_members_with_subcategories']
        self.assertEqual(list(site.categorymembers('Chess', results=15)), res)

    def test_cat_mems_wo_subcats(self):
        ''' test categorymember without subcategories '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['category_members_without_subcategories']
        ctm = site.categorymembers('Chess', results=15, subcategories=False)
        self.assertEqual(list(ctm), res)

    def test_cat_mems_w_subcats_lim(self):
        ''' test categorymember without subcategories limited '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['category_members_without_subcategories_5']
        ctm = site.categorymembers('Chess', results=5, subcategories=False)
        self.assertEqual(list(ctm), res)
        self.assertEqual(len(res), 5)


class TestMediaWikiExceptions(unittest.TestCase):
    ''' Test MediaWiki Exceptions '''
    def test_page_error(self):
        ''' Test that page error is thrown correctly '''
        site = MediaWikiOverloaded()
        self.assertRaises(PageError, lambda: site.page('gobbilygook'))

    def test_page_error_message(self):
        ''' Test that page error is thrown correctly '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        try:
            site.page('gobbilygook')
        except PageError as ex:
            self.assertEqual(ex.message, response['page_error_msg'])

    def test_page_error_pageid(self):
        ''' Test that page error is thrown correctly pageid'''
        site = MediaWikiOverloaded()
        self.assertRaises(PageError, lambda: site.page(pageid=-1))

    def test_page_error_message_pageid(self):
        ''' Test that page error is thrown correctly '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        try:
            site.page(pageid=-1)
        except PageError as ex:
            self.assertEqual(ex.message, response['page_error_msg_pageid'])

    def test_page_error_none_message(self):
        ''' test if neither pageid or title is present '''
        try:
            raise PageError(pageid=None, title=None)
        except PageError as ex:
            msg = (u'"{0}" does not match any pages. Try another '
                   'query!').format('')
            self.assertEqual(ex.message, msg)

    def test_redirect_error(self):
        ''' Test that redirect error is thrown correctly '''
        site = MediaWikiOverloaded(url='http://awoiaf.westeros.org/api.php')
        self.assertRaises(RedirectError,
                          lambda: site.page('arya', auto_suggest=False,
                                            redirect=False))

    def test_redirect_error_msg(self):
        ''' Test that redirect error is thrown correctly '''
        site = MediaWikiOverloaded(url='http://awoiaf.westeros.org/api.php')
        response = site.responses[site.api_url]
        try:
            site.page('arya', auto_suggest=False, redirect=False)
        except RedirectError as ex:
            self.assertEqual(ex.message, response['redirect_error_msg'])

    def test_disambiguation_error(self):
        ''' Test that disambiguation error is thrown correctly '''
        site = MediaWikiOverloaded()
        self.assertRaises(DisambiguationError, lambda: site.page('bush'))

    def test_disambiguation_error_msg(self):
        ''' Test that disambiguation error is thrown correctly '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        try:
            site.page('bush')
        except DisambiguationError as ex:
            self.assertEqual(ex.message, response['disambiguation_error_msg'])

    def test_geocoord_error(self):
        ''' test geocoord error thrown '''
        site = MediaWikiOverloaded()
        invalid = Decimal('-9999999999.999')
        self.assertRaises(MediaWikiGeoCoordError,
                          lambda: site.geosearch(latitude=invalid,
                                                 longitude=Decimal('0.0'),
                                                 results=22, radius=10000))

    def test_geocoord_error_msg(self):
        ''' test that the error geo error message is correct '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        try:
            site.geosearch(latitude=Decimal('-9999999999.999'),
                           longitude=Decimal('0.0'), results=22, radius=10000)
        except MediaWikiGeoCoordError as ex:
            self.assertEqual(ex.message, response['invalid_lat_long_geo_msg'])

    def test_geocoord_value_error(self):
        ''' test value error being thrown correctly '''
        site = MediaWikiOverloaded()
        self.assertRaises(ValueError,
                          lambda: site.geosearch(latitude=None,
                                                 longitude=Decimal('0.0'),
                                                 results=22, radius=10000))

    def test_geocoord_value_error_msg(self):
        ''' test that the error value error message is correct '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        try:
            site.geosearch(latitude=None, longitude=Decimal('0.0'),
                           results=22, radius=10000)
        except ValueError as ex:
            self.assertEqual(str(ex), response['invalid_lat_long_value_msg'])

    def test_api_url_error(self):
        ''' test changing api url to invalid throws exception '''
        site = MediaWikiOverloaded()
        url = 'http://french.wikipedia.org/w/api.php'
        self.assertRaises(MediaWikiAPIURLError,
                          lambda: site.set_api_url(api_url=url, lang='fr'))

    def test_api_url_error_msg(self):
        ''' test api url error message on set '''
        site = MediaWikiOverloaded()
        url = 'http://french.wikipedia.org/w/api.php'
        try:
            site.set_api_url(api_url=url, lang='fr')
        except MediaWikiAPIURLError as ex:
            response = site.responses[site.api_url]
            self.assertEqual(ex.message, response['api_url_error_msg'])

    def test_api_url_on_init_error(self):
        ''' test api url error on init '''
        url = 'http://french.wikipedia.org/w/api.php'
        self.assertRaises(MediaWikiAPIURLError,
                          lambda: MediaWikiOverloaded(url=url, lang='fr'))

    def test_api_url_on_init_error_msg(self):
        ''' test api url error message on init '''
        site = MediaWikiOverloaded()  # something to use to lookup results
        url = 'http://french.wikipedia.org/w/api.php'
        try:
            MediaWikiOverloaded(url=url, lang='fr')
        except MediaWikiAPIURLError as ex:
            response = site.responses[url]
            self.assertEqual(ex.message, response['api_url_error_msg'])

    def test_http_timeout_msg(self):
        ''' test the http timeout message '''
        query = 'gobbilygook'
        try:
            raise HTTPTimeoutError(query)
        except HTTPTimeoutError as ex:
            msg = ('Searching for "{0}" resulted in a timeout. Try '
                   'again in a few seconds, and ensure you have rate '
                   'limiting set to True.').format(query)
            self.assertEqual(ex.message, msg)

    def test_http_mediawiki_error_msg(self):
        ''' test the mediawiki error message '''
        error = 'Unknown Error'
        try:
            raise HTTPTimeoutError(error)
        except HTTPTimeoutError as ex:
            msg = (u'Searching for "{0}" resulted in a timeout. Try '
                   'again in a few seconds, and ensure you have rate '
                   'limiting set to True.').format(error)
            self.assertEqual(ex.message, msg)

    def test_mediawiki_exception(self):
        ''' throw MediaWikiBaseException '''
        def func():
            ''' test function '''
            raise MediaWikiException('new except!')
        self.assertRaises(MediaWikiException,
                          func)

    def test_mediawiki_exception_msg(self):
        ''' test that base msg is retained '''
        error = 'Unknown Error'
        try:
            raise MediaWikiException(error)
        except MediaWikiException as ex:
            msg = ('An unknown error occured: "{0}". Please report '
                   'it on GitHub!').format(error)
            self.assertEqual(ex.message, msg)

    def test_mediawiki_except_msg_str(self):
        ''' test that base msg is retained '''
        error = 'Unknown Error'
        try:
            raise MediaWikiException(error)
        except MediaWikiException as ex:
            msg = ('An unknown error occured: "{0}". Please report '
                   'it on GitHub!').format(error)
            self.assertEqual(str(ex), msg)

    def test_check_err_res_http_msg(self):
        ''' test check query by throwing specific errors '''
        site = MediaWikiOverloaded()
        response = dict()
        response['error'] = dict()
        response['error']['info'] = 'HTTP request timed out.'
        query = 'something'
        try:
            site._check_error_response(response, query)
        except HTTPTimeoutError as ex:
            msg = (u'Searching for "{0}" resulted in a timeout. Try '
                   'again in a few seconds, and ensure you have rate '
                   'limiting set to True.').format(query)
            self.assertEqual(str(ex), msg)

    def test_check_err_res_http(self):
        ''' test check query by throwing specific errors '''
        site = MediaWikiOverloaded()
        response = dict()
        response['error'] = dict()
        response['error']['info'] = 'HTTP request timed out.'
        query = 'something'
        self.assertRaises(HTTPTimeoutError,
                          lambda: site._check_error_response(response, query))

    def test_check_er_res_media_msg(self):
        ''' test check query by throwing specific error message ; mediawiki '''
        site = MediaWikiOverloaded()
        response = dict()
        response['error'] = dict()
        response['error']['info'] = 'blah blah'
        query = 'something'
        try:
            site._check_error_response(response, query)
        except MediaWikiException as ex:
            msg = ('An unknown error occured: "{0}". Please report '
                   'it on GitHub!').format(response['error']['info'])
            self.assertEqual(str(ex), msg)

    def test_check_err_res_media(self):
        ''' test check query by throwing specific errors; mediawiki '''
        site = MediaWikiOverloaded()
        response = dict()
        response['error'] = dict()
        response['error']['info'] = 'blah blah'
        query = 'something'
        self.assertRaises(MediaWikiException,
                          lambda: site._check_error_response(response, query))

    def test_check_query_err(self):
        ''' test _check_query value error '''
        site = MediaWikiOverloaded()
        query = None
        msg = 'Query must be specified'
        self.assertRaises(ValueError, lambda: site._check_query(query, msg))

    def test_check_query_err_msg(self):
        ''' test _check_query value error message '''
        site = MediaWikiOverloaded()
        query = None
        msg = 'Query must be specified'
        try:
            site._check_query(query, msg)
        except ValueError as ex:
            self.assertEqual(str(ex), msg)


class TestMediaWikiRequests(unittest.TestCase):
    ''' test the actual wiki_request '''
    def test_wiki_request(self):
        ''' test wiki request by testing the timing.... '''
        site = MediaWikiOverloaded()
        # self.assertEqual(site._rate_limit_last_call, None)
        site.rate_limit = True
        site.rate_limit_min_wait = timedelta(seconds=2)
        site.search('chest set')
        start_time = site._rate_limit_last_call
        site.opensearch('new york')
        site.prefixsearch('ar')
        end_time = site._rate_limit_last_call
        self.assertGreater(end_time - start_time, timedelta(seconds=2))
        self.assertNotEqual(site._rate_limit_last_call, None)


class TestMediaWikiPage(unittest.TestCase):
    ''' Test MediaWiki Pages '''
    def setUp(self):
        api_url = 'http://awoiaf.westeros.org/api.php'
        self.site = MediaWikiOverloaded(url=api_url)
        self.response = self.site.responses[self.site.api_url]
        self.pag = self.site.page('arya')

    def test_page_value_err_msg(self):
        ''' test that ValueError message thrown from random'''
        site = MediaWikiOverloaded()
        try:
            site.page()
        except ValueError as ex:
            msg = 'Either a title or a pageid must be specified'
            self.assertEqual(str(ex), msg)

    def test_page_value_err(self):
        ''' test that ValueError is thrown from random'''
        site = MediaWikiOverloaded()
        self.assertRaises(ValueError, lambda: site.page(None))

    def test_page_title(self):
        ''' Test a page title '''
        self.assertEqual(self.pag.title, self.response['arya']['title'])

    def test_page_pageid(self):
        ''' Test a page pageid '''
        self.assertEqual(self.pag.pageid, self.response['arya']['pageid'])

    def test_page_url(self):
        ''' Test a page url '''
        self.assertEqual(self.pag.url, self.response['arya']['url'])

    def test_page_backlinks(self):
        ''' Test a page backlinks '''
        self.assertEqual(self.pag.backlinks,
                         self.response['arya']['backlinks'])

    def test_page_images(self):
        ''' Test a page imsages '''
        self.assertEqual(self.pag.images, self.response['arya']['images'])

    def test_page_redirects(self):
        ''' Test a page redirects '''
        self.assertEqual(self.pag.redirects,
                         self.response['arya']['redirects'])

    def test_page_links(self):
        ''' Test a page links '''
        self.assertEqual(self.pag.links, self.response['arya']['links'])

    def test_page_categories(self):
        ''' Test a page categories '''
        self.assertEqual(self.pag.categories,
                         self.response['arya']['categories'])

    def test_page_references(self):
        ''' Test a page references '''
        self.assertEqual(self.pag.references,
                         self.response['arya']['references'])

    def test_page_content(self):
        ''' Test a page content '''
        self.assertEqual(self.pag.content,
                         self.response['arya']['content'])

    def test_page_parent_id(self):
        ''' Test a page parent_id '''
        self.assertEqual(self.pag.parent_id,
                         self.response['arya']['parent_id'])

    def test_page_revision_id(self):
        ''' Test a page revision_id '''
        self.assertEqual(self.pag.revision_id,
                         self.response['arya']['revision_id'])

    def test_page_coordinates_none(self):
        ''' Test a page coordinates none '''
        self.assertEqual(self.pag.coordinates,
                         self.response['arya']['coordinates'])

    def test_page_sections(self):
        ''' Test a page sections '''
        self.assertEqual(self.pag.sections,
                         self.response['arya']['sections'])

    def test_page_section(self):
        ''' Test a page returning a section '''
        self.assertEqual(self.pag.section('A Game of Thrones'),
                         self.response['arya']['section_a_game_of_thrones'])

    def test_page_last_section(self):
        ''' Test a page returning the last section '''
        self.assertEqual(self.pag.section('External links'),
                         self.response['arya']['last_section'])

    def test_page_invalid_section(self):
        ''' Test a page invalid section '''
        self.assertEqual(self.pag.section('gobbilygook'), None)

    def test_page_summary(self):
        ''' test page summary '''
        self.assertEqual(self.pag.summary, self.response['arya']['summary'])

    def test_page_html(self):
        ''' test page html '''
        self.assertEqual(self.pag.html, self.response['arya']['html'])

    def test_page_repr(self):
        ''' test page representation '''
        self.assertEqual(str(self.pag), '''<MediaWikiPage 'Arya Stark'>''')

    def test_page_eq(self):
        ''' test page equality '''
        tmp = self.site.page('arya')
        self.assertEqual(self.pag == tmp, True)

    def test_page_redirect(self):
        ''' test page redirect '''
        tmp = self.site.page('arya', auto_suggest=False)
        self.assertEqual(self.pag == tmp, True)

    def test_page_redirect_pageid(self):
        ''' test page redirect from page id '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        pag = site.page(pageid=24337758, auto_suggest=False)
        self.assertEqual(str(pag), "<MediaWikiPage 'BPP (complexity)'>")
        self.assertEqual(int(pag.pageid), 4079)
        self.assertEqual(pag.title, 'BPP (complexity)')

    def test_page_neq(self):
        ''' test page inequality '''
        tmp = self.site.page('jon snow')
        self.assertEqual(self.pag == tmp, False)
        self.assertEqual(self.pag != tmp, True)

    def test_page_neq_attr_err(self):
        ''' test page inequality by AttributeError '''
        tmp = self.site.page('arya')
        del tmp.__dict__['pageid']  # force AttributeError
        self.assertEqual(self.pag != tmp, True)

    def test_page_preload(self):
        ''' test preload of page properties '''
        pag = self.site.page('arya', preload=True)
        self.assertEqual(hasattr(pag, '_content'), True)
        self.assertEqual(hasattr(pag, '_summary'), True)
        self.assertEqual(hasattr(pag, '_images'), True)
        self.assertEqual(hasattr(pag, '_references'), True)
        self.assertEqual(hasattr(pag, '_links'), True)
        self.assertEqual(hasattr(pag, '_sections'), True)
        self.assertEqual(hasattr(pag, '_redirects'), True)
        self.assertEqual(hasattr(pag, '_coordinates'), True)
        self.assertEqual(hasattr(pag, '_backlinks'), True)
        self.assertEqual(hasattr(pag, '_categories'), True)
