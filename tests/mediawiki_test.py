# -*- coding: utf-8 -*-
'''
Unittest class
'''
from __future__ import (unicode_literals, absolute_import, print_function)
import sys
import time
import unittest
import json
from datetime import (timedelta)
from decimal import (Decimal)

from mediawiki import (MediaWiki, MediaWikiPage, PageError, RedirectError,
                       DisambiguationError, MediaWikiAPIURLError,
                       MediaWikiGeoCoordError, HTTPTimeoutError,
                       MediaWikiException, MediaWikiCategoryTreeError,
                       MediaWikiLoginError)
import mediawiki
from .utilities import find_depth, FunctionUseCounter


if sys.version_info[0] >= 3:
    unicode = str


class MediaWikiOverloaded(MediaWiki):
    ''' Overload the MediaWiki class to change how wiki_request works '''
    def __init__(self, url='https://{lang}.wikipedia.org/w/api.php', lang='en',
                 timeout=15, rate_limit=False,
                 rate_limit_wait=timedelta(milliseconds=50),
                 cat_prefix='Category', user_agent=None):
        ''' new init '''

        with open('./tests/mock_requests.json', 'r') as file_handle:
            self.requests = json.load(file_handle)
        with open('./tests/mock_responses.json', 'r') as file_handle:
            self.responses = json.load(file_handle)
        self.tree_path = './tests/mock_categorytree.json'

        MediaWiki.__init__(self, url=url, lang=lang, timeout=timeout,
                           rate_limit=rate_limit,
                           rate_limit_wait=rate_limit_wait,
                           cat_prefix=cat_prefix, user_agent=user_agent)

    def _get_response(self, params):
        ''' override the __get_response method '''
        new_params = json.dumps(tuple(sorted(params.items())))
        return self.requests[self.api_url][new_params]

    def _post_response(self, params):
        ''' override the __get_response method '''
        new_params = json.dumps(tuple(sorted(params.items())))
        return self.requests[self.api_url][new_params]


class TestMediaWiki(unittest.TestCase):
    ''' test the MediaWiki Class Basic functionality '''
    def test_version(self):
        ''' test version information '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.version, mediawiki.__version__)

    def test_api_url(self):
        ''' test the original api '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.api_url, 'https://en.wikipedia.org/w/api.php')

    def test_base_url(self):
        ''' test that the base url is parsed correctly '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.base_url, 'https://en.wikipedia.org')

    def test_base_url_no_http(self):
        ''' test that the base url is parsed correctly without http '''
        site = MediaWikiOverloaded(url='https://awoiaf.westeros.org/api.php')
        self.assertEqual(site.base_url, 'https://awoiaf.westeros.org')

    def test_base_url_switch(self):
        ''' test that the base url is parsed correctly when switching sites '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.base_url, 'https://en.wikipedia.org')
        site.set_api_url('https://awoiaf.westeros.org/api.php')
        self.assertEqual(site.base_url, 'https://awoiaf.westeros.org')

    def test_api_url_set(self):
        ''' test the api url being set at creation time '''
        site = MediaWikiOverloaded(url='https://awoiaf.westeros.org/api.php')
        response = site.responses[site.api_url]
        self.assertEqual(site.api_url, 'https://awoiaf.westeros.org/api.php')
        self.assertEqual(site.api_version, response['api_version'])
        self.assertEqual(sorted(site.extensions), sorted(response['extensions']))

    def test_change_lang(self):
        ''' test changing the language '''
        site = MediaWikiOverloaded()
        site.language = 'FR'
        self.assertEqual(site.language, 'fr')
        self.assertEqual(site.api_url, 'https://fr.wikipedia.org/w/api.php')

    def test_change_lang_same(self):
        ''' test changing the language to the same lang '''
        site = MediaWikiOverloaded(url='https://fr.wikipedia.org/w/api.php',
                                   lang='fr')
        site.language = 'FR'
        self.assertEqual(site.language, 'fr')
        self.assertEqual(site.api_url, 'https://fr.wikipedia.org/w/api.php')

    def test_api_lang_no_url(self):
        ''' test setting the language on init without api_url '''
        site = MediaWikiOverloaded(lang='fr')
        self.assertEqual(site.language, 'fr')
        self.assertEqual(site.api_url, 'https://fr.wikipedia.org/w/api.php')

    def test_api_lang_no_url_upper(self):
        ''' test setting the language on init without api_url upper case '''
        site = MediaWikiOverloaded(lang='FR')
        self.assertEqual(site.language, 'fr')
        self.assertEqual(site.api_url, 'https://fr.wikipedia.org/w/api.php')

    def test_change_lang_no_change(self):
        ''' test changing the language when url will not change '''
        site = MediaWikiOverloaded(url='https://awoiaf.westeros.org/api.php')
        site.language = 'FR'
        self.assertEqual(site.language, 'fr')
        self.assertEqual(site.api_url, 'https://awoiaf.westeros.org/api.php')

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
        self.assertEqual(site.api_url, 'https://en.wikipedia.org/w/api.php')
        self.assertEqual(site.api_version, response['api_version'])
        self.assertEqual(sorted(site.extensions), sorted(response['extensions']))

        site.set_api_url('https://awoiaf.westeros.org/api.php', lang='en')
        response = site.responses[site.api_url]
        self.assertEqual(site.api_url, 'https://awoiaf.westeros.org/api.php')
        self.assertEqual(site.api_version, response['api_version'])
        self.assertEqual(sorted(site.extensions), sorted(response['extensions']))

    def test_change_api_url_lang(self):
        ''' test changing the api url with only language '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.api_url, 'https://en.wikipedia.org/w/api.php')
        site.set_api_url(lang='fr')
        self.assertEqual(site.api_url, 'https://fr.wikipedia.org/w/api.php')
        self.assertEqual(site.language, 'fr')

    def test_change_api_url_lang_upper(self):
        ''' test changing the api url with only language upper case '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.api_url, 'https://en.wikipedia.org/w/api.php')
        site.set_api_url(lang='FR')
        self.assertEqual(site.api_url, 'https://fr.wikipedia.org/w/api.php')
        self.assertEqual(site.language, 'fr')

    def test_change_user_agent(self):
        ''' test changing the user agent '''
        site = MediaWikiOverloaded()
        site.user_agent = 'test-user-agent'
        self.assertEqual(site.user_agent, 'test-user-agent')

    def test_init_user_agent(self):
        ''' test initializing the user agent '''
        site = MediaWikiOverloaded(user_agent='test-user-agent')
        self.assertEqual(site.user_agent, 'test-user-agent')

    def test_languages(self):
        ''' test pulling wikimedia supported languages '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.supported_languages, response['languages'])

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
        ''' test default timeout '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.timeout, 15)

    def test_set_timeout(self):
        ''' test setting timeout '''
        site = MediaWikiOverloaded()
        site.timeout = 30
        self.assertEqual(site.timeout, 30)

    def test_set_timeout_none(self):
        ''' test setting timeout to None '''
        site = MediaWikiOverloaded()
        site.timeout = None
        self.assertEqual(site.timeout, None)

    def test_set_timeout_bad(self):
        ''' test that we raise the ValueError '''
        self.assertRaises(ValueError,
                          lambda: MediaWikiOverloaded(timeout='foo'))

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

    def test_no_memoized(self):
        ''' test changing the caching of results '''
        site = MediaWikiOverloaded()
        self.assertTrue(site.use_cache)
        site.use_cache = False
        self.assertFalse(site.use_cache)
        site.search('chest set')
        self.assertEqual(site.memoized, dict())
        site.use_cache = True
        site.search('chest set')
        self.assertNotEqual(site.memoized, dict())

    def test_refresh_interval(self):
        ''' test not setting refresh interval '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.refresh_interval, None)

    def test_refresh_interval_set(self):
        ''' test setting refresh interval '''
        site = MediaWikiOverloaded()
        site.refresh_interval = 5
        self.assertEqual(site.refresh_interval, 5)

    def test_refresh_interval_neg(self):
        ''' test setting refresh interval to invalid number '''
        site = MediaWikiOverloaded()
        site.refresh_interval = -5
        self.assertEqual(site.refresh_interval, None)

    def test_refresh_interval_str(self):
        ''' test setting refresh interval to invalid type '''
        site = MediaWikiOverloaded()
        site.refresh_interval = "something"
        self.assertEqual(site.refresh_interval, None)

    def test_memoized_refresh_no(self):
        ''' test refresh interval for memoized cache when too quick '''
        site = MediaWikiOverloaded()
        site.refresh_interval = 2
        site.search('chest set')
        key1 = list(site.memoized['search'])[0]  # get first key
        time1 = site.memoized['search'][key1]
        site.search('chest set')
        key2 = list(site.memoized['search'])[0]  # get first key
        time2 = site.memoized['search'][key2]
        self.assertEqual(time1, time2)

    def test_memoized_refresh(self):
        ''' test refresh interval for memoized cache '''
        site = MediaWikiOverloaded()
        site.refresh_interval = 2
        site.search('chest set')
        key1 = list(site.memoized['search'])[0]  # get first key
        time1 = site.memoized['search'][key1]
        time.sleep(5)
        site.search('chest set')
        key2 = list(site.memoized['search'])[0]  # get first key
        time2 = site.memoized['search'][key2]
        self.assertNotEqual(time1, time2)
        self.assertGreater(time2, time1)

    def test_cat_prefix(self):
        ''' test the default category prefix'''
        site = MediaWikiOverloaded()
        self.assertEqual(site.category_prefix, 'Category')

    def test_cat_prefix_change(self):
        ''' test changing the category prefix '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.category_prefix, 'Category')
        site.category_prefix = 'Something:'
        self.assertEqual(site.category_prefix, 'Something')

class TestMediaWikiLogin(unittest.TestCase):
    ''' Test login functionality '''

    def test_successful_login(self):
        ''' test login success!'''
        site = MediaWikiOverloaded()
        res = site.login('username', 'fakepassword')
        self.assertEqual(site.logged_in, True)
        self.assertEqual(res, True)

    def test_failed_login(self):
        ''' test that login failure throws the correct exception '''
        site = MediaWikiOverloaded()
        try:
            res = site.login('badusername', 'fakepassword')
        except MediaWikiLoginError as ex:
            self.assertEqual(site.logged_in, False)
            msg = 'MediaWiki login failure: Incorrect username or password entered. Please try again.'
            self.assertEqual(ex.error, msg)
        else:
            self.assertEqual(True, False)

    def test_failed_login_no_strict(self):
        ''' test that login failure with strict off works '''
        site = MediaWikiOverloaded()
        res = site.login('badusername', 'fakepassword', strict=False)
        self.assertEqual(site.logged_in, False)
        self.assertEqual(res, False)

class TestMediaWikiRandom(unittest.TestCase):
    ''' test Random Functionality '''
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


class TestMediaWikiAllPages(unittest.TestCase):
    ''' test Mediawiki AllPages functionality '''
    def test_allpages(self):
        ''' test using the all page query '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]['all_pages_query_a']

        res = site.allpages("a")
        self.assertEqual(response, res)

    def test_allpages_num_results(self):
        ''' test using the all page query with a limitting number '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]['all_pages_query_a_1']

        res = site.allpages("a", results=1)
        self.assertEqual(response, res)


class TestMediaWikiSearch(unittest.TestCase):
    ''' test MediaWiki Page Search Functionality '''
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
        self.assertEqual(site.search('chess set', results=3,
                                     suggestion=False),
                         response['search_with_suggestion_not_found_small'])
        num_res = len(response['search_with_suggestion_not_found_small'])
        self.assertEqual(num_res, 3)  # limit to 500

    def test_search_sug_not_found_lg(self):
        ''' test searching without suggestion limited to the correct number '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(site.search('chess set', results=505,
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
    ''' test GeoSearch Functionality '''
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
        self.assertEqual(site.geosearch(title='new york city',
                                        latitude=Decimal('-9999999999.999'),
                                        longitude=Decimal('0.0'), results=22,
                                        radius=10000),
                         response['geosearch_page_invalid_lat_long'])

    def test_geo_page_rad_res_set(self):
        ''' test geosearch with radius and result set '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.geosearch(title='new york city', results=22, radius=10000)
        self.assertEqual(res, response['geosearch_page_radius_results_set'])
        self.assertEqual(len(res), 22)

    def test_geo_page_rad_res(self):
        ''' test geosearch with radius set '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.geosearch(title='new york city', radius=10000)
        self.assertEqual(res, response['geosearch_page_radius_results'])
        self.assertEqual(len(res), 10)

    def test_geo_page(self):
        ''' test geosearch using just page '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = site.geosearch(title='new york city')
        self.assertEqual(res, response['geosearch_page'])
        self.assertEqual(len(res), 10)


class TestMediaWikiOpenSearch(unittest.TestCase):
    ''' test OpenSearch Functionality '''
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
    ''' test PrefixSearch Functionality '''
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


class TestMediaWikiSummary(unittest.TestCase):
    ''' test the summary functionality '''
    def test_summarize_chars(self):
        ''' test summarize number chars '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['summarize_chars_50']
        sumr = site.summary('chess', chars=50)
        self.assertEqual(res, sumr)
        self.assertEqual(len(res), 54)  # add the ellipses

    def test_summarize_sents(self):
        ''' test summarize number sentences '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['summarize_sent_5']
        sumr = site.summary('chess', sentences=5)
        self.assertEqual(res, sumr)
        # self.assertEqual(len(res), 466)

    def test_summarize_paragraph(self):
        ''' test summarize based on first section '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['summarize_first_paragraph']
        sumr = site.summary('chess')
        self.assertEqual(res, sumr)

    def test_page_summary_chars(self):
        ''' test page summarize - chars '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['summarize_chars_50']
        pag = site.page('chess')
        sumr = pag.summarize(chars=50)
        self.assertEqual(res, sumr)
        self.assertEqual(len(res), 54)

    def test_page_summary_sents(self):
        ''' test page summarize - sentences '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['summarize_sent_5']
        pag = site.page('chess')
        sumr = pag.summarize(sentences=5)
        self.assertEqual(res, sumr)
        # self.assertEqual(len(res), 466)


class TestMediaWikiCategoryMembers(unittest.TestCase):
    ''' test CategoryMember Functionality '''
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

    def test_cat_mems_very_large(self):
        ''' test category members that is larger than the max allowed '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['category_members_very_large']
        ctm = site.categorymembers('Disambiguation categories', results=None)
        self.assertEqual(list(ctm), res)
        self.assertEqual(len(res[0]), 0)
        self.assertEqual(len(res[1]), 1629)  # difficult if it changes sizes


class TestMediaWikiExceptions(unittest.TestCase):
    ''' test MediaWiki Exceptions '''
    def test_page_error(self):
        ''' test that page error is thrown correctly '''
        site = MediaWikiOverloaded()
        self.assertRaises(PageError, lambda: site.page('gobbilygook'))

    def test_page_error_message(self):
        ''' test that page error is thrown correctly '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        try:
            site.page('gobbilygook')
        except PageError as ex:
            self.assertEqual(ex.message, response['page_error_msg'])

    def test_page_error_pageid(self):
        ''' test that page error is thrown correctly pageid'''
        site = MediaWikiOverloaded()
        self.assertRaises(PageError, lambda: site.page(pageid=-1))

    def test_page_error_title(self):
        ''' test that page error is thrown correctly title'''
        site = MediaWikiOverloaded()
        self.assertRaises(PageError,
                          lambda: site.page(title='gobbilygook',
                                            auto_suggest=False))

    def test_page_error_title_msg(self):
        ''' test that page error is thrown correctly title'''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        try:
            site.page(title='gobbilygook', auto_suggest=False)
        except PageError as ex:
            self.assertEqual(ex.message, response['page_error_msg_title'])

    def test_page_error_message_pageid(self):
        ''' test that page error is thrown correctly '''
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
        ''' test that redirect error is thrown correctly '''
        site = MediaWikiOverloaded(url='https://awoiaf.westeros.org/api.php')
        self.assertRaises(RedirectError,
                          lambda: site.page('arya', auto_suggest=False,
                                            redirect=False))

    def test_redirect_error_msg(self):
        ''' test that redirect error is thrown correctly '''
        site = MediaWikiOverloaded(url='https://awoiaf.westeros.org/api.php')
        response = site.responses[site.api_url]
        try:
            site.page('arya', auto_suggest=False, redirect=False)
        except RedirectError as ex:
            self.assertEqual(ex.message, response['redirect_error_msg'])

    def test_disambiguation_error(self):
        ''' test that disambiguation error is thrown correctly '''
        site = MediaWikiOverloaded()
        self.assertRaises(DisambiguationError, lambda: site.page('bush'))

    def test_disambiguation_error_msg(self):
        ''' test that disambiguation error is thrown correctly '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        try:
            site.page('bush')
        except DisambiguationError as ex:
            self.assertEqual(ex.message, response['disambiguation_error_msg'])
            self.assertEqual(ex.title, 'Bush')
            self.assertEqual(ex.url, 'https://en.wikipedia.org/wiki/Bush')

    def test_disamb_error_msg_w_empty(self):
        ''' test that disambiguation error is thrown correctly and no
        IndexError is thrown '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        try:
            site.page('Oasis')
        except DisambiguationError as ex:
            self.assertEqual(ex.message,
                             response['disambiguation_error_msg_with_empty'])

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
        url = 'https://french.wikipedia.org/w/api.php'
        self.assertRaises(MediaWikiAPIURLError,
                          lambda: site.set_api_url(api_url=url, lang='fr'))

    def test_api_url_error_msg(self):
        ''' test api url error message on set '''
        site = MediaWikiOverloaded()
        url = 'https://french.wikipedia.org/w/api.php'
        try:
            site.set_api_url(api_url=url, lang='fr')
        except MediaWikiAPIURLError as ex:
            response = site.responses[site.api_url]
            self.assertEqual(ex.message, response['api_url_error_msg'])

    def test_api_url_on_init_error(self):
        ''' test api url error on init '''
        url = 'https://french.wikipedia.org/w/api.php'
        self.assertRaises(MediaWikiAPIURLError,
                          lambda: MediaWikiOverloaded(url=url, lang='fr'))

    def test_api_url_on_init_error_msg(self):
        ''' test api url error message on init '''
        site = MediaWikiOverloaded()  # something to use to lookup results
        url = 'https://french.wikipedia.org/w/api.php'
        try:
            MediaWikiOverloaded(url=url, lang='fr')
        except MediaWikiAPIURLError as ex:
            response = site.responses[site.api_url]
            self.assertEqual(ex.message, response['api_url_error_msg'])

    def test_api_url_on_error_reset(self):
        ''' test api url error resets to original URL '''
        site = MediaWikiOverloaded()  # something to use to lookup results
        url = 'https://french.wikipedia.org/w/api.php'
        wiki = 'https://en.wikipedia.org/w/api.php'
        try:
            MediaWikiOverloaded(url=url, lang='fr')
        except MediaWikiAPIURLError:
            self.assertNotEqual(site.api_url, url)
            self.assertEqual(site.api_url, wiki)

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
        ''' test throwing a MediaWikiBaseException '''
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
            msg = ('An unknown error occurred: "{0}". Please report '
                   'it on GitHub!').format(error)
            self.assertEqual(ex.message, msg)

    def test_mediawiki_except_msg_str(self):
        ''' test that base msg is retained '''
        error = 'Unknown Error'
        try:
            raise MediaWikiException(error)
        except MediaWikiException as ex:
            msg = ('An unknown error occurred: "{0}". Please report '
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
            msg = ('An unknown error occurred: "{0}". Please report '
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
    ''' test MediaWiki Pages '''
    def setUp(self):
        ''' single function for all the tests (well most of) '''
        api_url = 'https://awoiaf.westeros.org/api.php'
        self.site = MediaWikiOverloaded(url=api_url)
        self.response = self.site.responses[self.site.api_url]
        self.pag = self.site.page('arya')

    def test_call_directly(self):
        ''' test calling MediaWikiPage directly '''
        page = MediaWikiPage(self.site, title="arya")
        self.assertEqual(page.title, self.response['arya']['title'])

    def test_call_directly_error(self):
        ''' test calling MediaWikiPage directly with error message'''
        try:
            MediaWikiPage(self.site)
        except ValueError as ex:
            msg = 'Either a title or a pageid must be specified'
            self.assertEqual(str(ex), msg)

    def test_page_value_err(self):
        ''' test that ValueError is thrown when error calling mediawikipage
        directly '''
        self.assertRaises(ValueError, lambda: MediaWikiPage(self.site))

    def test_page_value_err_msg(self):
        ''' test that ValueError message thrown from random'''
        site = MediaWikiOverloaded()
        try:
            site.page()
        except ValueError as ex:
            msg = 'Either a title or a pageid must be specified'
            self.assertEqual(str(ex), msg)

    def test_page_value_err_none(self):
        ''' test that ValueError is thrown from None '''
        site = MediaWikiOverloaded()
        self.assertRaises(ValueError, lambda: site.page(None))

    def test_page_title(self):
        ''' test a page title '''
        self.assertEqual(self.pag.title, self.response['arya']['title'])

    def test_page_pageid(self):
        ''' test a page pageid '''
        self.assertEqual(self.pag.pageid, self.response['arya']['pageid'])

    def test_page_url(self):
        ''' test a page url '''
        self.assertEqual(self.pag.url, self.response['arya']['url'])

    def test_page_backlinks(self):
        ''' test a page backlinks '''
        self.assertEqual(self.pag.backlinks,
                         self.response['arya']['backlinks'])

    def test_page_images(self):
        ''' test a page imsages '''
        self.assertEqual(self.pag.images, self.response['arya']['images'])

    def test_page_redirects(self):
        ''' test a page redirects '''
        self.assertEqual(self.pag.redirects,
                         self.response['arya']['redirects'])

    def test_page_links(self):
        ''' test a page links '''
        self.assertEqual(self.pag.links, self.response['arya']['links'])

    def test_page_categories(self):
        ''' test a page categories '''
        self.assertEqual(self.pag.categories,
                         self.response['arya']['categories'])

    def test_page_references(self):
        ''' test a page references '''
        self.assertEqual(self.pag.references,
                         self.response['arya']['references'])

    def test_page_references_no_http(self):
        ''' test a page references with mixed http '''
        site = MediaWikiOverloaded()
        page = site.page('Minneapolis')
        response = site.responses[site.api_url]['references_without_http']
        self.assertEqual(page.references, response)

    def test_page_content(self):
        ''' test a page content '''
        self.assertEqual(self.pag.content,
                         self.response['arya']['content'])

    def test_page_parent_id(self):
        ''' test a page parent_id '''
        self.assertEqual(self.pag.parent_id,
                         self.response['arya']['parent_id'])

    def test_page_revision_id(self):
        ''' test a page revision_id '''
        self.assertEqual(self.pag.revision_id,
                         self.response['arya']['revision_id'])

    def test_page_coordinates_none(self):
        ''' test a page coordinates none '''
        self.assertEqual(self.pag.coordinates,
                         self.response['arya']['coordinates'])

    def test_page_coordinates(self):
        ''' test a page coordinates where found '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        pag = site.page('Washington Monument')
        coords = pag.coordinates
        self.assertEqual([str(coords[0]), str(coords[1])],
                         response['wash_mon'])

    def test_page_langlinks(self):
        ''' test a page language links property '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]['nobel_chemistry']['langlinks']
        pag = site.page('Nobel Prize in Chemistry')
        self.assertEqual(pag.langlinks, response)

    def test_page_sections(self):
        ''' test a page sections '''
        self.assertEqual(self.pag.sections,
                         self.response['arya']['sections'])

    def test_table_of_contents(self):
        ''' test a page table of contents '''

        def _flatten_toc(_dict, res):
            ''' flatten the table of contents into a list '''
            for key, val in _dict.items():
                res.append(key)
                if val.keys():
                    _flatten_toc(val, res)

        toc = self.pag.table_of_contents
        toc_ord = list()
        _flatten_toc(toc, toc_ord)
        self.assertEqual(toc_ord, self.response['arya']['sections'])

    def test_page_section(self):
        ''' test a page returning a section '''
        self.assertEqual(self.pag.section('A Game of Thrones'),
                         self.response['arya']['section_a_game_of_thrones'])

    def test_page_last_section(self):
        ''' test a page returning the last section '''
        self.assertEqual(self.pag.section('External links'),
                         self.response['arya']['last_section'])

    def test_page_single_section(self):
        ''' test a page returning the last section '''
        pag = self.site.page('Castos')
        self.assertEqual(pag.section('References and Notes'),
                         self.response['castos']['section'])

    def test_page_invalid_section(self):
        ''' test a page invalid section '''
        self.assertEqual(self.pag.section('gobbilygook'), None)

    def test_page_summary(self):
        ''' test page summary '''
        self.assertEqual(self.pag.summary, self.response['arya']['summary'])

    def test_page_html(self):
        ''' test page html '''
        self.assertEqual(self.pag.html, self.response['arya']['html'])

    def test_page_str(self):
        ''' test page string representation '''
        self.assertEqual(str(self.pag), '''<MediaWikiPage 'Arya Stark'>''')

    def test_page_repr(self):
        ''' test page repr without unicode '''
        self.assertEqual(repr(self.pag), '''<MediaWikiPage 'Arya Stark'>''')

    def test_page_unicode(self):
        ''' test with unicode representation '''
        site = MediaWikiOverloaded()
        page = site.page('Jacques Léonard Muller')
        if sys.version_info < (3, 0):
            self.assertEqual(unicode(page),
                             '''<MediaWikiPage 'Jacques Léonard Muller'>''')
        else:
            self.assertEqual(str(page),
                             '''<MediaWikiPage 'Jacques Léonard Muller'>''')

    def test_page_repr_2(self):
        ''' test page string representation '''
        site = MediaWikiOverloaded()
        page = site.page('Jacques Léonard Muller')
        name = u'''<MediaWikiPage 'Jacques Léonard Muller'>'''
        if sys.version_info > (3, 0):
            res = repr(page)
        else:
            res = unicode(page)
        self.assertEqual(res, name)

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
        delattr(tmp, 'pageid')
        self.assertEqual(self.pag != tmp, True)

    def test_page_preload(self):
        ''' test preload of page properties '''
        pag = self.site.page('arya', preload=True)
        self.assertNotEqual(getattr(pag, '_content'), None)
        self.assertNotEqual(getattr(pag, '_summary'), None)
        self.assertNotEqual(getattr(pag, '_images'), None)
        self.assertNotEqual(getattr(pag, '_references'), None)
        self.assertNotEqual(getattr(pag, '_links'), None)
        self.assertNotEqual(getattr(pag, '_sections'), None)
        self.assertNotEqual(getattr(pag, '_redirects'), None)
        self.assertNotEqual(getattr(pag, '_coordinates'), False)
        self.assertNotEqual(getattr(pag, '_backlinks'), None)
        self.assertNotEqual(getattr(pag, '_categories'), None)

    def test_page_no_preload(self):
        ''' test page properties that are not set '''
        pag = self.site.page('arya', preload=False)
        self.assertEqual(getattr(pag, '_content'), None)
        self.assertEqual(getattr(pag, '_summary'), None)
        self.assertEqual(getattr(pag, '_images'), None)
        self.assertEqual(getattr(pag, '_references'), None)
        self.assertEqual(getattr(pag, '_links'), None)
        self.assertEqual(getattr(pag, '_sections'), None)
        self.assertEqual(getattr(pag, '_redirects'), None)
        self.assertEqual(getattr(pag, '_coordinates'), False)
        self.assertEqual(getattr(pag, '_backlinks'), None)
        self.assertEqual(getattr(pag, '_categories'), None)

    def test_full_sections_large(self):
        ''' test parsing a set of sections - large '''
        wiki = MediaWikiOverloaded()
        pg = wiki.page('New York City')
        response = wiki.responses[wiki.api_url]
        self.assertEqual(pg.sections, response['new_york_city_sections'])

    def test_table_of_contents_large(self):
        ''' test a page table of contents for nested TOC - large'''

        def _flatten_toc(_dict, res):
            ''' flatten the table of contents into a list '''
            for key, val in _dict.items():
                res.append(key)
                if val.keys():
                    _flatten_toc(val, res)
        wiki = MediaWikiOverloaded()
        response = wiki.responses[wiki.api_url]
        pg = wiki.page('New York City')
        toc = pg.table_of_contents
        toc_ord = list()
        _flatten_toc(toc, toc_ord)
        self.assertEqual(toc_ord, response['new_york_city_sections'])

    def test_page_section_large(self):
        ''' test a page returning a section - large '''
        wiki = MediaWikiOverloaded()
        response = wiki.responses[wiki.api_url]
        pg = wiki.page('New York City')
        self.assertEqual(pg.section('Air quality'), response['new_york_city_air_quality'])

    def test_page_last_section_large(self):
        ''' test a page returning the last section - large '''
        wiki = MediaWikiOverloaded()
        response = wiki.responses[wiki.api_url]
        pg = wiki.page('New York City')
        self.assertEqual(pg.section('External links'), response['new_york_city_last_sec'])


class TestMediaWikiCategoryTree(unittest.TestCase):
    ''' test the category tree functionality '''

    def test_double_category_tree(self):
        ''' test category tree using a list '''
        site = MediaWikiOverloaded()
        with open(site.tree_path, 'r') as fpt:
            res = json.load(fpt)
        cat = site.categorytree(['Chess', 'Ebola'], depth=None)
        self.assertEqual(cat, res)

    def test_triple_category_tree_none(self):
        ''' test category tree using a list but one is blank or None '''
        site = MediaWikiOverloaded()
        with open(site.tree_path, 'r') as fpt:
            res = json.load(fpt)
        cat = site.categorytree(['Chess', 'Ebola', None], depth=None)
        self.assertEqual(cat, res)

    def test_triple_category_tree_bnk(self):
        ''' test category tree using a list but one is blank or None '''
        site = MediaWikiOverloaded()
        with open(site.tree_path, 'r') as fpt:
            res = json.load(fpt)
        cat = site.categorytree(['Chess', 'Ebola', ''], depth=None)
        self.assertEqual(cat, res)

    def test_single_category_tree_list(self):
        ''' test category tree using a list with one element '''
        site = MediaWikiOverloaded()
        with open(site.tree_path, 'r') as fpt:
            res = json.load(fpt)
        cat = site.categorytree(['Chess'], depth=None)
        self.assertEqual(cat['Chess'], res['Chess'])

    def test_single_category_tree_str(self):
        ''' test category tree using a string '''
        site = MediaWikiOverloaded()
        with open(site.tree_path, 'r') as fpt:
            res = json.load(fpt)
        cat = site.categorytree('Ebola', depth=None)
        self.assertEqual(cat['Ebola'], res['Ebola'])

    def test_category_tree_valerror_1(self):
        ''' test category provided None throws error '''
        site = MediaWikiOverloaded()
        self.assertRaises(ValueError,
                          lambda: site.categorytree(None, depth=None))

    def test_cattree_error_msg_1(self):
        ''' test that ValueError message when None passed as category '''
        site = MediaWikiOverloaded()
        category = None
        try:
            site.categorytree(category, depth=None)
        except ValueError as ex:
            msg = ("CategoryTree: Parameter 'category' must either "
                   "be a list of one or more categories or a string; "
                   "provided: '{}'".format(category))
            self.assertEqual(str(ex), msg)

    def test_category_tree_valerror_2(self):
        ''' test category provided empty str throws error '''
        site = MediaWikiOverloaded()
        self.assertRaises(ValueError,
                          lambda: site.categorytree('', depth=None))

    def test_cattree_error_msg_2(self):
        ''' test that ValueError message when '' passed as category: 2 '''
        site = MediaWikiOverloaded()
        category = ''
        try:
            site.categorytree(category, depth=None)
        except ValueError as ex:
            msg = ("CategoryTree: Parameter 'category' must either "
                   "be a list of one or more categories or a string; "
                   "provided: '{}'".format(category))
            self.assertEqual(str(ex), msg)

    def test_category_tree_valerror_3(self):
        ''' test category provided empty str throws error '''
        site = MediaWikiOverloaded()
        self.assertRaises(ValueError,
                          lambda: site.categorytree('Chess', depth=0))

    def test_cattree_error_msg_3(self):
        ''' test that ValueError message when depth < 1 '''
        site = MediaWikiOverloaded()
        try:
            site.categorytree('Chess', depth=0)
        except ValueError as ex:
            msg = ("CategoryTree: Parameter 'depth' must be either None "
                   "(for the full tree) or be greater than 0")
            self.assertEqual(str(ex), msg)

    def test_depth_none_1(self):
        ''' test the depth when going full depth '''
        site = MediaWikiOverloaded()
        cat = site.categorytree(['Chess'], depth=None)
        depth = find_depth(cat['Chess'])
        self.assertEqual(depth, 7)

    def test_depth_none_2(self):
        ''' test the depth when going full depth take two '''
        site = MediaWikiOverloaded()
        cat = site.categorytree(['Ebola'], depth=None)
        depth = find_depth(cat['Ebola'])
        self.assertEqual(depth, 1)

    def test_depth_limited(self):
        ''' test the depth when going partial depth '''
        site = MediaWikiOverloaded()
        cat = site.categorytree(['Chess'], depth=5)
        depth = find_depth(cat['Chess'])
        self.assertEqual(depth, 5)

    def test_depth_limited_2(self):
        ''' test the depth when going partial depth take two '''
        site = MediaWikiOverloaded()
        cat = site.categorytree(['Chess'], depth=2)
        depth = find_depth(cat['Chess'])
        self.assertEqual(depth, 2)

    def test_cattree_list_with_none(self):
        ''' test the removing None or '' categories from the list '''
        site = MediaWikiOverloaded()
        cat = site.categorytree(['Chess', None], depth=2)
        depth = find_depth(cat['Chess'])
        self.assertEqual(depth, 2)
        self.assertEqual(len(cat.keys()), 1)

    def test_badcat_tree_pageerror(self):
        ''' test category provided bad category throws error '''
        site = MediaWikiOverloaded()
        self.assertRaises(PageError, lambda: site.categorytree('Chess Ebola'))

    def test_badcat_error_msg(self):
        ''' test that ValueError message when depth < 1 '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]['missing_categorytree']
        category = 'Chess Ebola'
        try:
            site.categorytree(category)
        except PageError as ex:
            self.assertEqual(str(ex), res)

    def test_unretrievable_cat(self):
        ''' test throwing the exception when cannot retrieve category tree '''
        def new_cattreemem():
            ''' force exception to be thrown '''
            raise Exception

        site = MediaWikiOverloaded()
        site.categorymembers = new_cattreemem
        self.assertRaises(MediaWikiCategoryTreeError,
                          lambda: site.categorytree('Chess'))

    def test_unretrievable_cat_msg(self):
        ''' test the exception message when cannot retrieve category tree '''
        def new_cattreemem():
            ''' force exception to be thrown '''
            raise Exception

        category = 'Chess'
        msg = ("Categorytree threw an exception for trying to get the "
               "same category '{}' too many times. Please try again later "
               "and perhaps use the rate limiting option.").format(category)
        site = MediaWikiOverloaded()
        site.categorymembers = new_cattreemem
        try:
            site.categorytree(category)
        except MediaWikiCategoryTreeError as ex:
            self.assertEqual(str(ex), msg)
            self.assertEqual(ex.category, 'Chess')


class TestMediaWikiLogos(unittest.TestCase):
    ''' Add logo tests here '''

    def test_logo_present(self):
        ''' test when single logo or main image present '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]
        page = site.page('Chess')
        self.assertEqual(page.logos, res['chess_logos'])

    def test_mult_logo_present(self):
        ''' test when multiple main images or logos present '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]
        page = site.page('Sony Music')
        self.assertEqual(page.logos, res['sony_music_logos'])

    def test_infobox_not_present(self):
        ''' test when no infobox (based on the class name) is found '''
        site = MediaWikiOverloaded()
        page = site.page('Antivirus Software')
        self.assertEqual(page.logos, list())  # should be an empty list


class TestMediaWikiHatnotes(unittest.TestCase):
    ''' Test the pulling of hatnotes from mediawiki pages '''

    def test_contains_hatnotes(self):
        ''' Test when hatnotes are present '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]
        page = site.page('Chess')
        self.assertEqual(page.hatnotes, res['chess_hatnotes'])

    def test_no_hatnotes(self):
        ''' Test when no hatnote is on the page '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]
        page_name = ('List of Battlestar Galactica (1978 TV series) and '
                     'Galactica 1980 episodes')
        page = site.page(page_name)
        self.assertEqual(page.hatnotes, res['page_no_hatnotes'])


class TestMediaWikiParseSectionLinks(unittest.TestCase):
    ''' Test the pulling of links from the parse section links '''

    def test_contains_ext_links(self):
        ''' Test when external links are present '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]
        page = site.page('''McDonald's''')
        tmp = page.parse_section_links('External links')
        for i, item in enumerate(tmp):
            tmp[i] = list(item)
        self.assertEqual(tmp, res['mcy_ds_external_links'])

    def test_contains_ext_links_2(self):
        ''' Test when external links are present capitalization '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]
        page = site.page('''McDonald's''')
        tmp = page.parse_section_links('EXTERNAL LINKS')
        for i, item in enumerate(tmp):
            tmp[i] = list(item)
        self.assertEqual(tmp, res['mcy_ds_external_links'])

    def test_no_ext_links(self):
        ''' Test when no external links on the page '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]
        page = site.page('Tropical rainforest conservation')
        self.assertEqual(page.parse_section_links('External links'), None)

    def test_song_ice_and_fire_links(self):
        site = MediaWikiOverloaded('https://awoiaf.westeros.org/api.php')
        res = site.responses[site.api_url]
        pg = site.page('arya')

        for section in pg.sections:
            links = pg.parse_section_links(section)
            for i, item in enumerate(links):
                links[i] = list(item)
            self.assertEqual(links, res['arya_{}_links'.format(section)])


class TestMediaWikiRegressions(unittest.TestCase):
    ''' Add regression tests here for special cases '''

    def test_hidden_file(self):
        ''' test hidden file or no url: issue #14 '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]
        page = site.page('One Two Three... Infinity')
        try:
            page.images
        except KeyError:
            self.fail("KeyError exception on hidden file")
        self.assertEqual(page.images, res['hidden_images'])

    def test_large_cont_query(self):
        ''' test known large continued query with continue='||' '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]['large_continued_query']
        page = site.page('List of named minor planets (numerical)')
        self.assertEqual(page.links, res)

    def test_large_cont_query_images(self):
        ''' test known large continued query with images '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]['large_continued_query_images']
        page = site.page('B8 polytope')
        self.assertEqual(page.images, res)
        self.assertEqual(len(page.images), 2214)

    def test_infinit_loop_images(self):
        ''' test known image infinite loop: issue #15 '''
        site = MediaWikiOverloaded()
        res = site.responses[site.api_url]['infinite_loop_images']
        page = site.page('Rober Eryol')
        site._get_response = FunctionUseCounter(site._get_response)
        self.assertEqual(page.images, res)
        self.assertEqual(site._get_response.count, 13)

    def test_missing_title_disambig(self):
        ''' test when title not present for disambiguation error '''
        site = MediaWikiOverloaded()
        res0 = site.responses[site.api_url]['missing_title_disamb_dets']
        res1 = site.responses[site.api_url]['missing_title_disamb_msg']

        try:
            page = site.page('Leaching')
        except DisambiguationError as ex:
            self.assertEqual(ex.details, res0)
            self.assertEqual(str(ex), res1)
        else:
            self.assertEqual(True, False)

    def test_query_continue(self):
        site = MediaWikiOverloaded(url='https://practicalplants.org/w/api.php')
        res = site.responses[site.api_url]['query-continue-find']

        cat_membs = site.categorymembers('Plant', results=None, subcategories=False)
        self.assertEqual(cat_membs, res)
        self.assertEqual(len(cat_membs), 7415)


class TestMediaWikiUtilities(unittest.TestCase):
    ''' some of the utility functions should be tested '''

    def test_relative_url(self):
        ''' tests of the relative url function '''
        url1 = 'http://www.google.com'
        url2 = 'ftp://somewhere.out.there'
        url3 = '//cdn.somewhere.out.there/over.js'
        url4 = '/wiki/Chess'
        url5 = '#Chess_board'  # internal to same page
        self.assertEqual(mediawiki.utilities.is_relative_url(url1), False)
        self.assertEqual(mediawiki.utilities.is_relative_url(url2), False)
        self.assertEqual(mediawiki.utilities.is_relative_url(url3), False)
        self.assertEqual(mediawiki.utilities.is_relative_url(url4), True)
        self.assertEqual(mediawiki.utilities.is_relative_url(url5), None)
