'''
Unittest class
'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mediawiki import (MediaWiki, PageError, RedirectError,
                       DisambiguationError)
import unittest
import pickle
from datetime import timedelta


class MediaWikiOverloaded(MediaWiki):
    ''' Overload the MediaWiki class to change how wiki_request works '''
    def __init__(self, url='http://en.wikipedia.org/w/api.php', lang='en',
                 timeout=None, rate_limit=False,
                 rate_limit_wait=timedelta(milliseconds=50)):
        with open('./tests/mock_api_data.p', 'rb') as file_handle:
            self.data = pickle.load(file_handle)
        MediaWiki.__init__(self, url=url, lang=lang, timeout=timeout,
                           rate_limit=rate_limit,
                           rate_limit_wait=rate_limit_wait)

    def wiki_request(self, params):
        ''' override the wiki requests to pull from the mock data '''
        new_params = tuple(sorted(params.items()))
        return self.data[self.api_url]['query'][new_params]


class TestMediaWiki(unittest.TestCase):
    ''' Test the Media Wiki Class '''
    ##########################################
    # BASIC MediaWiki SITE FUNCTIONALITY TESTS
    ##########################################
    def test_api_url(self):
        ''' test the original api '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.api_url, 'http://en.wikipedia.org/w/api.php')

    def test_api_url_set(self):
        ''' test the api url being set at creation time '''
        site = MediaWikiOverloaded(url='http://awoiaf.westeros.org/api.php')
        self.assertEqual(site.api_url, 'http://awoiaf.westeros.org/api.php')
        self.assertEqual(site.api_version, site.data[site.api_url]['data']['api_version'])
        self.assertEqual(site.extensions, site.data[site.api_url]['data']['extensions'])

    def test_change_lang(self):
        ''' test changing the language '''
        site = MediaWikiOverloaded()
        site.language = 'FR'
        self.assertEqual(site.language, 'fr')
        self.assertEqual(site.api_url, 'http://fr.wikipedia.org/w/api.php')

    def test_api_version(self):
        ''' test api version parsed correctly'''
        site = MediaWikiOverloaded()
        self.assertEqual(site.api_version, site.data[site.api_url]['data']['api_version'])

    def test_extensions(self):
        ''' test parsing extensions correctly '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.extensions, site.data[site.api_url]['data']['extensions'])

    def test_change_api_url(self):
        ''' test switching the api url '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.api_url, 'http://en.wikipedia.org/w/api.php')
        self.assertEqual(site.api_version, site.data[site.api_url]['data']['api_version'])
        self.assertEqual(site.extensions, site.data[site.api_url]['data']['extensions'])

        site.set_api_url('http://awoiaf.westeros.org/api.php', lang='en')
        self.assertEqual(site.api_url, 'http://awoiaf.westeros.org/api.php')
        self.assertEqual(site.api_version, site.data[site.api_url]['data']['api_version'])
        self.assertEqual(site.extensions, site.data[site.api_url]['data']['extensions'])

    def test_change_user_agent(self):
        ''' test changing the user agent '''
        site = MediaWikiOverloaded()
        site.user_agent = 'test-user-agent'
        self.assertEqual(site.user_agent, 'test-user-agent')

    def test_languages(self):
        ''' test pulling wikimedia supported languages '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.languages(), site.data[site.api_url]['data']['languages'])

    ##########################################
    # TEST RANDOM FUNCTIONALITY
    ##########################################
    def test_random_2(self):
        ''' test pulling random pages '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.random(pages=2), site.data[site.api_url]['data']['random_2'])

    def test_random_10(self):
        ''' test pulling random pages '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.random(pages=10), site.data[site.api_url]['data']['random_10'])

    def test_random_202(self):
        ''' test pulling 202 random pages '''
        site = MediaWikiOverloaded()
        self.assertEqual(set(site.random(pages=202)), set(site.data[site.api_url]['data']['random_202']))
        print("\nNOTE: This is supposed to be limited to 20 by the API, per the documentation, but it isn't...")
        self.assertEqual(len(site.data[site.api_url]['data']['random_202']), 202)  # limit to 20

    ##########################################
    # TEST SEARCH FUNCTIONALITY
    ##########################################
    def test_search_no_sug(self):
        ''' test searching without suggestion '''
        site = MediaWikiOverloaded()
        # test that default is suggestion False
        api_url = site.data[site.api_url]['data']['search_without_suggestion']
        sws = site.data[site.api_url]['data']['search_without_suggestion']
        self.assertEqual(site.search('chest set'), api_url)
        self.assertEqual(site.search('chest set', suggestion=False), sws)

    def test_search_sug_found(self):
        ''' test searching with suggestion where found '''
        site = MediaWikiOverloaded()
        sws = site.data[site.api_url]['data']['search_with_suggestion_found']
        self.assertEqual(site.search('chest set', suggestion=True), sws)

    def test_search_sug_not_found(self):
        ''' test searching with suggestion where not found '''
        site = MediaWikiOverloaded()
        swsnf = site.data[site.api_url]['data']['search_with_suggestion_not_found']
        self.assertEqual(site.search('chess set', suggestion=True), swsnf)

    def test_search_sug_not_found_num(self):
        ''' test searching with suggestion where not found but limited to the correct number'''
        site = MediaWikiOverloaded()
        self.assertEqual(site.search('chess set', results=505, suggestion=False), site.data[site.api_url]['data']['search_with_suggestion_not_found_number'])
        self.assertEqual(len(site.data[site.api_url]['data']['search_with_suggestion_not_found_number']), 500)  # limit to 500

    ##########################################
    # TEST CATEGORYMEMBERS FUNCTIONALITY
    ##########################################
    def test_cat_mems_with_subcats(self):
        ''' test categorymember with subcategories '''
        site = MediaWikiOverloaded()
        res = site.data[site.api_url]['data']['category_members_with_subcategories']
        self.assertEqual(site.categorymembers("Chess", results=15, subcategories=True), res)

    def test_cat_mems_subcat_default(self):
        ''' test categorymember with default subcategories (True) '''
        site = MediaWikiOverloaded()
        res = site.data[site.api_url]['data']['category_members_with_subcategories']
        self.assertEqual(site.categorymembers("Chess", results=15), res)

    def test_cat_mems_wo_subcats(self):
        ''' test categorymember without subcategories '''
        site = MediaWikiOverloaded()
        res = site.data[site.api_url]['data']['category_members_without_subcategories']
        self.assertEqual(site.categorymembers("Chess", results=15, subcategories=False), res)

    def test_cat_mems_w_subcats_lim(self):
        ''' test categorymember without subcategories limited '''
        site = MediaWikiOverloaded()
        res = site.data[site.api_url]['data']['category_members_without_subcategories_5']
        self.assertEqual(site.categorymembers("Chess", results=5, subcategories=False), res)
        self.assertEqual(len(res), 5)

    ##########################################
    # TEST EXCEPTIONS FUNCTIONALITY
    ##########################################
    def test_page_error(self):
        ''' Test that page error is thrown correctly '''
        site = MediaWikiOverloaded()
        error = lambda: site.page('gobbilygook')
        self.assertRaises(PageError, error)

    def test_page_error_message(self):
        ''' Test that page error is thrown correctly '''
        site = MediaWikiOverloaded()
        error = lambda: site.page('gobbilygook')
        try:
            error()
        except PageError as ex:
            self.assertEqual(ex.message, site.data[site.api_url]['data']['page_error_msg'])

    def test_redirect_error(self):
        ''' Test that redirect error is thrown correctly '''
        site = MediaWikiOverloaded(url='http://awoiaf.westeros.org/api.php')
        error = lambda: site.page('arya', auto_suggest=False, redirect=False)
        self.assertRaises(RedirectError, error)

    def test_redirect_error_msg(self):
        ''' Test that redirect error is thrown correctly '''
        site = MediaWikiOverloaded(url='http://awoiaf.westeros.org/api.php')
        error = lambda: site.page('arya', auto_suggest=False, redirect=False)
        try:
            error()
        except RedirectError as ex:
            self.assertEqual(ex.message, site.data[site.api_url]['data']['redirect_error_msg'])

    def test_disambiguation_error(self):
        ''' Test that disambiguation error is thrown correctly '''
        site = MediaWikiOverloaded()
        error = lambda: site.page('bush')
        self.assertRaises(DisambiguationError, error)

    def test_disambiguation_error_msg(self):
        ''' Test that disambiguation error is thrown correctly '''
        site = MediaWikiOverloaded()
        error = lambda: site.page('bush')
        try:
            error()
        except DisambiguationError as ex:
            self.assertEqual(ex.message, site.data[site.api_url]['data']['disambiguation_error_msg'])
