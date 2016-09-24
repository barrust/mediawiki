'''
Unittest class
'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mediawiki import (MediaWiki, PageError, RedirectError,
                       DisambiguationError)
import unittest
import json
from datetime import timedelta


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

    def wiki_request(self, params):
        ''' override the wiki requests to pull from the mock data '''
        # json dumping to make python 2.7 tests work correctly
        new_params = json.dumps(tuple(sorted(params.items())))
        return self.requests[self.api_url][new_params]


class TestMediaWiki(unittest.TestCase):
    ''' Test the MediaWiki Class Basic functionality '''
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


class TestMediaWikiRandom(unittest.TestCase):
    ''' Test Random Functionality '''
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

    def test_search_sug_not_found_small_limit(self):
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        self.assertEqual(
                         site.search('chess set', results=3,
                                     suggestion=False),
                         response['search_with_suggestion_not_found_small'])
        num_res = len(response['search_with_suggestion_not_found_small'])
        self.assertEqual(num_res, 3)  # limit to 500

    def test_search_sug_not_found_large_limit(self):
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


# class TestMediaWikiSuggest(unittest.TestCase):


# class TestMediaWikiGeoSearch(unittest.TestCase):


# class TestMediaWikiOpenSearch(unittest.TestCase):


# class TestMediaWikiPrefixSearch(unittest.TestCase):


# class TestMediaWikiSummary(unittest.TestCase):


# class TestMediaWikiCategoryTree(unittest.TestCase):


class TestMediaWikiCategoryMembers(unittest.TestCase):
    ''' Test CategoryMember Functionality '''
    def test_cat_mems_with_subcats(self):
        ''' test categorymember with subcategories '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['category_members_with_subcategories']
        ctm = site.categorymembers("Chess", results=15, subcategories=True)
        self.assertEqual(list(ctm), res)  # list since json doesn't keep tuple

    def test_cat_mems_subcat_default(self):
        ''' test categorymember with default subcategories (True) '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['category_members_with_subcategories']
        self.assertEqual(list(site.categorymembers("Chess", results=15)), res)

    def test_cat_mems_wo_subcats(self):
        ''' test categorymember without subcategories '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['category_members_without_subcategories']
        ctm = site.categorymembers("Chess", results=15, subcategories=False)
        self.assertEqual(list(ctm), res)

    def test_cat_mems_w_subcats_lim(self):
        ''' test categorymember without subcategories limited '''
        site = MediaWikiOverloaded()
        response = site.responses[site.api_url]
        res = response['category_members_without_subcategories_5']
        ctm = site.categorymembers("Chess", results=5, subcategories=False)
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

    # def test_geocoord_error(self):
    #     pass
    # def test_geocoord_error_msg(self):
    #     pass
    # def test_geocoord_value_error(self):
    #     pass
    # def test_geocoord_value_error_msg(self):
    #     pass
    # def test_api_url_error(self):
    #     pass
    # def test_api_url_error_msg(self):
    #     pass
    # def test_api_url_on_init_error(self):
    #     pass
    # def test_api_url_on_init_error_msg(self):
    #     pass




class TestMediaWikiPage(unittest.TestCase):
    ''' Test MediaWiki Pages '''
    def test_page_and_properties(self):
        ''' Test a page from ASOIAF wiki with all properties '''
        site = MediaWikiOverloaded(url='http://awoiaf.westeros.org/api.php')
        response = site.responses[site.api_url]
        pag = site.page('arya')
        self.assertEqual(pag.title, response['arya']['title'])
        self.assertEqual(pag.pageid, response['arya']['pageid'])
        self.assertEqual(pag.url, response['arya']['url'])
        self.assertEqual(pag.backlinks, response['arya']['backlinks'])
        self.assertEqual(pag.images, response['arya']['images'])
        self.assertEqual(pag.redirects, response['arya']['redirects'])
        self.assertEqual(pag.links, response['arya']['links'])
        self.assertEqual(pag.categories, response['arya']['categories'])
        self.assertEqual(pag.references, response['arya']['references'])
        self.assertEqual(pag.content, response['arya']['content'])
        self.assertEqual(pag.parent_id, response['arya']['parent_id'])
        self.assertEqual(pag.revision_id, response['arya']['revision_id'])
        self.assertEqual(pag.coordinates, response['arya']['coordinates'])
        self.assertEqual(pag.sections, response['arya']['sections'])
        self.assertEqual(pag.section("A Game of Thrones"),
                         response['arya']['section_a_game_of_thrones'])
