from mediawiki import *
from .api_url_mock import api_url_mock
import unittest


class MediaWikiOverloaded(MediaWiki):
    def __init__(self):
        MediaWiki.__init__(self)

    def _wiki_request(self, params):
        ''' override the wiki requests to pull from the mock data '''
        new_params = tuple(sorted(params.items()))
        return api_url_mock[self.api_url][new_params]


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
        self.assertEqual(site.api_version, api_url_mock[site.api_url]['api-version'])

    def test_extensions(self):
        ''' test parsing extensions correctly '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.extensions, api_url_mock[site.api_url]['extensions'])

    def test_change_api_url(self):
        ''' test switching the api url '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.api_url, 'http://en.wikipedia.org/w/api.php')
        self.assertEqual(site.api_version, api_url_mock[site.api_url]['api-version'])
        self.assertEqual(site.extensions, api_url_mock[site.api_url]['extensions'])

        site.set_api_url('http://awoiaf.westeros.org/api.php', lang='en')
        self.assertEqual(site.api_url, 'http://awoiaf.westeros.org/api.php')
        self.assertEqual(site.api_version, api_url_mock[site.api_url]['api-version'])
        self.assertEqual(site.extensions, api_url_mock[site.api_url]['extensions'])

    def test_change_user_agent(self):
        ''' test changing the user agent '''
        site = MediaWikiOverloaded()
        site.user_agent = 'test-user-agent'
        self.assertEqual(site.user_agent, 'test-user-agent')

    def test_languages(self):
        ''' test pulling wikimedia supported languages '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.languages(), api_url_mock[site.api_url]['languages'])

    def test_random(self):
        ''' test pulling random pages '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.random(pages=2), api_url_mock[site.api_url]['two-random'])

    ##########################################
    # TEST SEARCH FUNCTIONALITY
    ##########################################
    def test_search_no_suggest(self):
        ''' test searching without suggestion '''
        site = MediaWikiOverloaded()
        # test that default is suggestion False
        self.assertEqual(site.search('chest set'), api_url_mock[site.api_url]['search-without-suggestion'])
        self.assertEqual(site.search('chest set', suggestion=False), api_url_mock[site.api_url]['search-without-suggestion'])

    def test_search_suggest_found(self):
        ''' test searching with suggestion where found '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.search('chest set', suggestion=True), api_url_mock[site.api_url]['search-with-suggestion-found'])

    def test_search_suggest_not_found(self):
        ''' test searching with suggestion where not found '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.search('chess set', suggestion=True), api_url_mock[site.api_url]['search-with-suggestion-not-found'])
