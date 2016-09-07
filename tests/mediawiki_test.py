'''
Unittest class
'''
from mediawiki import (MediaWiki)
# from .api_url_mock import api_url_mock
import unittest
import pickle
from datetime import datetime, timedelta


class MediaWikiOverloaded(MediaWiki):
    def __init__(self, url='http://en.wikipedia.org/w/api.php', lang='en',
                 timeout=None, rate_limit=False,
                 rate_limit_wait=timedelta(milliseconds=50)):
        with open('./tests/mock_api_data.p', 'rb') as f:
            self.data = pickle.load(f)
        MediaWiki.__init__(self)

    def _wiki_request(self, params):
        ''' override the wiki requests to pull from the mock data '''
        new_params = tuple(sorted(params.items()))
        return self.data[self.api_url]['query'][new_params]


class TestMediaWiki(unittest.TestCase):
    ##########################################
    # BASIC MediaWiki SITE FUNCTIONALITY TESTS
    ##########################################
    def test_api_url(self):
        ''' test the original api '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.api_url, 'http://en.wikipedia.org/w/api.php')

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
    def test_search_no_suggest(self):
        ''' test searching without suggestion '''
        site = MediaWikiOverloaded()
        # test that default is suggestion False
        self.assertEqual(site.search('chest set'), site.data[site.api_url]['data']['search_without_suggestion'])
        self.assertEqual(site.search('chest set', suggestion=False), site.data[site.api_url]['data']['search_without_suggestion'])

    def test_search_suggest_found(self):
        ''' test searching with suggestion where found '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.search('chest set', suggestion=True), site.data[site.api_url]['data']['search_with_suggestion_found'])

    def test_search_suggest_not_found(self):
        ''' test searching with suggestion where not found '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.search('chess set', suggestion=True), site.data[site.api_url]['data']['search_with_suggestion_not_found'])

    def test_search_suggest_not_found_number(self):
        ''' test searching with suggestion where not found but limited to the correct number'''
        site = MediaWikiOverloaded()
        self.assertEqual(site.search('chess set', results=505, suggestion=False), site.data[site.api_url]['data']['search_with_suggestion_not_found_number'])
        self.assertEqual(len(site.data[site.api_url]['data']['search_with_suggestion_not_found_number']), 500)  # limit to 500

    ##########################################
    # TEST CATEGORYMEMBERS FUNCTIONALITY
    ##########################################
