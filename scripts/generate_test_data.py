'''
Generate data for tests
'''
from __future__ import print_function
import sys
import os
from datetime import timedelta
import json
from decimal import Decimal
sys.path.insert(0, '../mediawiki')
from mediawiki import (MediaWiki, PageError, RedirectError,
                       DisambiguationError, MediaWikiAPIURLError,
                       MediaWikiGeoCoordError)


# set up the json objects
REQUESTS_FILE = './tests/mock_requests.json'
RESPONSES_FILE = './tests/mock_responses.json'
CATTREE_FILE = './tests/mock_categorytree.json'


def capture_response(func):
    ''' capture_response decorator to be used for tests '''
    def wrapper(*args, **kwargs):
        ''' define the actions '''
        file_path = os.path.abspath(REQUESTS_FILE)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as mock:
                mock_data = json.load(mock)
        else:
            mock_data = dict()

        new_params = json.dumps(tuple(sorted(args[1].items())))
        # build out parts of the dictionary
        if args[0].api_url not in mock_data:
            mock_data[args[0].api_url] = dict()
        try:
            res = func(*args, **kwargs)
        except Exception:
            res = dict()
        mock_data[args[0].api_url][new_params] = res
        with open(file_path, 'w') as mock:
            json.dump(mock_data, mock, ensure_ascii=False, indent=1,
                      sort_keys=True)
        return res
    return wrapper


class MediaWikiOverloaded(MediaWiki):
    ''' overloaded mediawiki class '''
    def __init__(self, url='https://{lang}.wikipedia.org/w/api.php', lang='en',
                 timeout=None, rate_limit=False,
                 rate_limit_wait=timedelta(milliseconds=50)):
        ''' overloaded init '''
        MediaWiki.__init__(self, url=url, lang=lang, timeout=timeout,
                           rate_limit=rate_limit,
                           rate_limit_wait=rate_limit_wait)

    @capture_response
    def _get_response(self, params):
        ''' overloaded response '''
        return MediaWiki._get_response(self, params)

    @capture_response
    def _post_response(self, params):
        ''' overloaded response '''
        return MediaWiki._post_response(self, params)


PULL_ALL = False

# Parameters to determine which tests to pull
PULL_SEARCHES = False
PULL_ALLPAGES = False
PULL_RANDOM = False
PULL_SUGGEST = False
PULL_OPENSEARCH = False
PULL_PREFIXSEARCH = False
PULL_GEOSEARCH = False
PULL_CATEGORYMEMBERS = False
PULL_CATEGORYTREE = False
PULL_SUMMARY = False
PULL_PAGE_ERRORS = False
PULL_DISAMBIGUATION_ERRORS = False
PULL_API_URL_ERROR = False
PULL_REDIRECT_ERROR = False
PULL_PAGES = False
PULL_LOGOS = False
PULL_HATNOTES = False
PULL_SECTION_LINKS = False
PULL_TABLE_OF_CONTENTS = False
PULL_LOGIN = False

# regression tests
PULL_ISSUE_15 = False
PULL_ISSUE_14 = False
PULL_ISSUE_35 = False
PULL_ISSUE_39 = False

# make files if they don't exist
if not os.path.isfile(REQUESTS_FILE):
    with open(REQUESTS_FILE, 'w') as file_handle:
        json.dump(dict(), file_handle, ensure_ascii=False)

if os.path.isfile(RESPONSES_FILE):
    with open(RESPONSES_FILE, 'r') as file_handle:
        responses = json.load(file_handle)
else:
    responses = dict()


# Begin building out new data objects
site = MediaWikiOverloaded()
french_site = MediaWikiOverloaded(url='https://fr.wikipedia.org/w/api.php',
                                  lang='fr')
asoiaf = MediaWikiOverloaded(url='https://awoiaf.westeros.org/api.php',
                             lang='fr')
plants = MediaWikiOverloaded(url='https://practicalplants.org/w/api.php')
wikipedia = MediaWikiOverloaded()


# ensure these pieces of information do not throw errors
if site.api_url not in responses:
    responses[site.api_url] = dict()
if french_site.api_url not in responses:
    responses[french_site.api_url] = dict()
if asoiaf.api_url not in responses:
    responses[asoiaf.api_url] = dict()

# pull in standard information for all sites (every time)
if site.api_url not in responses:
    responses[site.api_url] = dict()
responses[site.api_url]['api'] = site.api_url
responses[site.api_url]['lang'] = site.language
responses[site.api_url]['languages'] = site.supported_languages
responses[site.api_url]['api_version'] = site.api_version
responses[site.api_url]['extensions'] = site.extensions

if french_site.api_url not in responses:
    responses[french_site.api_url] = dict()
responses[french_site.api_url]['api'] = french_site.api_url
responses[french_site.api_url]['lang'] = french_site.language
responses[french_site.api_url]['languages'] = french_site.supported_languages
responses[french_site.api_url]['api_version'] = french_site.api_version
responses[french_site.api_url]['extensions'] = french_site.extensions

if asoiaf.api_url not in responses:
    responses[asoiaf.api_url] = dict()
responses[asoiaf.api_url]['api'] = asoiaf.api_url
responses[asoiaf.api_url]['lang'] = asoiaf.language
responses[asoiaf.api_url]['languages'] = asoiaf.supported_languages
responses[asoiaf.api_url]['api_version'] = asoiaf.api_version
responses[asoiaf.api_url]['extensions'] = asoiaf.extensions

if plants.api_url not in responses:
    responses[plants.api_url] = dict()

print("Completed basic mediawiki information")

if PULL_ALL is True or PULL_SEARCHES is True:
    res = site.search('chest set', suggestion=False)
    responses[site.api_url]['search_without_suggestion'] = res
    res = site.search('chest set', suggestion=True)
    responses[site.api_url]['search_with_suggestion_found'] = res
    res = site.search('chess set', suggestion=True)
    responses[site.api_url]['search_with_suggestion_not_found'] = res
    res = site.search('chess set', results=505, suggestion=False)
    responses[site.api_url]['search_with_suggestion_not_found_large'] = res
    res = site.search('chess set', results=3, suggestion=False)
    responses[site.api_url]['search_with_suggestion_not_found_small'] = res

    print("Completed pulling searches")

if PULL_ALL is True or PULL_ALLPAGES is True:
    res = site.allpages('a')
    responses[site.api_url]['all_pages_query_a'] = res

    res = site.allpages("a", results=1)
    responses[site.api_url]['all_pages_query_a_1'] = res

    print("Completed pulling allpages")

if PULL_ALL is True or PULL_RANDOM is True:
    responses[site.api_url]['random_1'] = site.random(pages=1)
    responses[site.api_url]['random_2'] = site.random(pages=2)
    responses[site.api_url]['random_10'] = site.random(pages=10)
    responses[site.api_url]['random_202'] = site.random(pages=202)

    print("Completed pulling random pages")

if PULL_ALL is True or PULL_SUGGEST is True:
    responses[site.api_url]['suggest_chest_set'] = site.suggest("chest set")
    responses[site.api_url]['suggest_chess_set'] = site.suggest("chess set")
    responses[site.api_url]['suggest_new_york'] = site.suggest('new york')
    responses[site.api_url]['suggest_yonkers'] = site.suggest('yonkers')
    responses[site.api_url]['suggest_no_results'] = site.suggest('gobbilygook')

    print("Completed pulling suggestions")

if PULL_ALL is True or PULL_OPENSEARCH is True:
    res = site.opensearch('new york')
    responses[site.api_url]['opensearch_new_york'] = res
    res = site.opensearch('new york', results=5)
    responses[site.api_url]['opensearch_new_york_result'] = res
    res = site.opensearch('new york', redirect=False)
    responses[site.api_url]['opensearch_new_york_redirect'] = res
    res = site.opensearch('new york', results=5, redirect=False)
    responses[site.api_url]['opensearch_new_york_result_redirect'] = res

    print("Completed pulling open searches")

if PULL_ALL is True or PULL_PREFIXSEARCH is True:
    responses[site.api_url]['prefixsearch_ar'] = site.prefixsearch('ar')
    responses[site.api_url]['prefixsearch_ba'] = site.prefixsearch('ba')
    res = site.prefixsearch('ba', results=5)
    responses[site.api_url]['prefixsearch_ba_5'] = res
    res = site.prefixsearch('ba', results=30)
    responses[site.api_url]['prefixsearch_ba_30'] = res

    print("Completed pulling prefix searches")

if PULL_ALL is True or PULL_GEOSEARCH is True:
    res = site.geosearch(latitude=Decimal('0.0'), longitude=Decimal('0.0'))
    responses[site.api_url]['geosearch_decimals'] = res
    res = site.geosearch(latitude=Decimal('0.0'), longitude=0.0)
    responses[site.api_url]['geosearch_mix_types'] = res
    res = site.geosearch(title='new york city', latitude=Decimal('-9999999999.999'),
                         longitude=Decimal('0.0'), results=22, radius=10000)
    responses[site.api_url]['geosearch_page_invalid_lat_long'] = res
    res = site.geosearch(title='new york city', results=22, radius=10000)
    responses[site.api_url]['geosearch_page_radius_results_set'] = res
    res = site.geosearch(title='new york city', radius=10000)
    responses[site.api_url]['geosearch_page_radius_results'] = res
    res = site.geosearch(title='new york city')
    responses[site.api_url]['geosearch_page'] = res
    try:
        site.geosearch(latitude=None, longitude=Decimal('0.0'), results=22,
                       radius=10000)
    except (ValueError) as ex:
        responses[site.api_url]['invalid_lat_long_value_msg'] = str(ex)
    try:
        site.geosearch(latitude=Decimal('-9999999999.999'),
                       longitude=Decimal('0.0'), results=22, radius=10000)
    except (MediaWikiGeoCoordError) as ex:
        responses[site.api_url]['invalid_lat_long_geo_msg'] = ex.message

    print("Completed pulling geo search")

if PULL_ALL is True or PULL_CATEGORYMEMBERS is True:
    res = site.categorymembers("Chess", results=15, subcategories=True)
    responses[site.api_url]['category_members_with_subcategories'] = res
    res = site.categorymembers("Chess", results=15, subcategories=False)
    responses[site.api_url]['category_members_without_subcategories'] = res
    res = site.categorymembers("Chess", results=5, subcategories=False)
    responses[site.api_url]['category_members_without_subcategories_5'] = res
    res = site.categorymembers('Disambiguation categories', results=None)
    responses[site.api_url]['category_members_very_large'] = res

    print("Completed pulling category members")

if PULL_ALL is True or PULL_CATEGORYTREE is True:
    site.rate_limit = True
    ct = site.categorytree(['Chess', 'Ebola'], depth=None)
    with open(CATTREE_FILE, 'w') as fp:
        json.dump(ct, fp, ensure_ascii=False, sort_keys=True)

    try:
        site.categorytree('Chess Ebola', depth=None)
    except Exception as ex:
        responses[site.api_url]['missing_categorytree'] = str(ex)
    site.rate_limit = False

    print("Completed pulling category tree")

if PULL_ALL is True or PULL_SUMMARY is True:
    res = site.summary('chess', chars=50)
    responses[site.api_url]['summarize_chars_50'] = res
    res = site.summary('chess', sentences=5)
    responses[site.api_url]['summarize_sent_5'] = res
    res = site.summary('chess')
    responses[site.api_url]['summarize_first_paragraph'] = res

    print("Completed pulling summaries")

if PULL_ALL is True or PULL_PAGE_ERRORS is True:
    try:
        site.page('gobbilygook')
    except PageError as ex:
        responses[site.api_url]['page_error_msg'] = ex.message

    try:
        site.page('gobbilygook', auto_suggest=False)
    except PageError as ex:
        responses[site.api_url]['page_error_msg_title'] = ex.message

    try:
        site.page(pageid=-1)
    except PageError as ex:
        responses[site.api_url]['page_error_msg_pageid'] = ex.message

    print("Completed pulling page errors")

if PULL_ALL is True or PULL_DISAMBIGUATION_ERRORS is True:
    try:
        site.page('bush')
    except DisambiguationError as ex:
        responses[site.api_url]['disambiguation_error_msg'] = ex.message

    try:
        site.page('Oasis')
    except DisambiguationError as ex:
        msg = ex.message
        responses[site.api_url]['disambiguation_error_msg_with_empty'] = msg

    print("Completed pulling disambiguation errors")

if PULL_ALL is True or PULL_API_URL_ERROR is True:
    url = 'https://french.wikipedia.org/w/api.php'
    try:
        site.set_api_url(api_url=url, lang='fr')
    except MediaWikiAPIURLError as ex:
        responses[site.api_url]['api_url_error_msg'] = ex.message

    # this shouldn't be necessary since it should go back to the original
    # values
    site.set_api_url(api_url='https://en.wikipedia.org/w/api.php', lang='en')
    print("Completed pulling api url errors")

if PULL_ALL is True or PULL_REDIRECT_ERROR is True:
    # print('Start redirect error')
    try:
        asoiaf.page('arya', auto_suggest=False, redirect=False)
    except RedirectError as ex:
        responses[asoiaf.api_url]['redirect_error_msg'] = ex.message

    print("Completed pulling redirect errors")


if PULL_ALL is True or PULL_PAGES is True:
    # unicode
    site.page(u"Jacques Léonard Muller")
    # page id
    site.page(pageid=24337758, auto_suggest=False)

    # coordinates
    p = site.page('Washington Monument')
    coords = p.coordinates
    responses[site.api_url]['wash_mon'] = [str(coords[0]), str(coords[1])]

    # page properties

    # arya
    pg = asoiaf.page('arya')
    responses[asoiaf.api_url]['arya'] = dict()
    responses[asoiaf.api_url]['arya']['title'] = pg.title
    responses[asoiaf.api_url]['arya']['pageid'] = pg.pageid
    responses[asoiaf.api_url]['arya']['revision_id'] = pg.revision_id
    responses[asoiaf.api_url]['arya']['parent_id'] = pg.parent_id
    responses[asoiaf.api_url]['arya']['content'] = pg.content
    responses[asoiaf.api_url]['arya']['url'] = pg.url
    # other properties
    responses[asoiaf.api_url]['arya']['backlinks'] = pg.backlinks
    responses[asoiaf.api_url]['arya']['images'] = pg.images
    responses[asoiaf.api_url]['arya']['redirects'] = pg.redirects
    responses[asoiaf.api_url]['arya']['links'] = pg.links
    responses[asoiaf.api_url]['arya']['categories'] = pg.categories
    responses[asoiaf.api_url]['arya']['references'] = pg.references
    responses[asoiaf.api_url]['arya']['content'] = pg.content
    responses[asoiaf.api_url]['arya']['parent_id'] = pg.parent_id
    responses[asoiaf.api_url]['arya']['revision_id'] = pg.revision_id
    responses[asoiaf.api_url]['arya']['coordinates'] = pg.coordinates
    responses[asoiaf.api_url]['arya']['summary'] = pg.summary
    responses[asoiaf.api_url]['arya']['sections'] = pg.sections
    res = pg.section('A Game of Thrones')
    responses[asoiaf.api_url]['arya']['section_a_game_of_thrones'] = res
    res = pg.section('External links')
    responses[asoiaf.api_url]['arya']['last_section'] = res
    responses[asoiaf.api_url]['arya']['html'] = pg.html

    # jon snow
    pg = asoiaf.page('jon snow')
    responses[asoiaf.api_url]['jon-snow'] = dict()
    responses[asoiaf.api_url]['jon-snow']['title'] = pg.title
    responses[asoiaf.api_url]['jon-snow']['pageid'] = pg.pageid
    responses[asoiaf.api_url]['jon-snow']['revision_id'] = pg.revision_id
    responses[asoiaf.api_url]['jon-snow']['parent_id'] = pg.parent_id
    responses[asoiaf.api_url]['jon-snow']['content'] = pg.content
    responses[asoiaf.api_url]['jon-snow']['url'] = pg.url

    # castos
    pg = asoiaf.page('Castos')
    responses[asoiaf.api_url]['castos'] = dict()
    res = pg.section('References and Notes')
    responses[asoiaf.api_url]['castos']['section'] = res

    # other pages as they will be in the response object
    asoiaf.page('arya', auto_suggest=False)

    # lang links property (standard wikipedia)
    pg = site.page('Nobel Prize in Chemistry')
    responses[site.api_url]['nobel_chemistry'] = dict()
    responses[site.api_url]['nobel_chemistry']['langlinks'] = pg.langlinks

    print("Completed pulling pages and properties")


if PULL_ALL is True or PULL_LOGOS is True:
    # single logo
    res = wikipedia.page('Chess').logos
    responses[wikipedia.api_url]['chess_logos'] = res
    # multiple logos
    res = wikipedia.page('Sony Music').logos
    responses[wikipedia.api_url]['sony_music_logos'] = res
    # no infobox
    res = wikipedia.page('Antivirus Software').logos
    responses[wikipedia.api_url]['antivirus_software_logos'] = res

    print("Completed pulling logos")

if PULL_ALL is True or PULL_HATNOTES is True:
    # contains hatnotes
    res = wikipedia.page('Chess').hatnotes
    responses[wikipedia.api_url]['chess_hatnotes'] = res
    # no hatnotes
    page_name = ('List of Battlestar Galactica (1978 TV series) and '
                 'Galactica 1980 episodes')
    res = wikipedia.page(page_name).hatnotes
    responses[wikipedia.api_url]['page_no_hatnotes'] = res

    print("Completed pulling hat notes")

if PULL_ALL is True or PULL_SECTION_LINKS is True:
    # contains external links
    pg = wikipedia.page('''McDonald's''')
    res = pg.parse_section_links('EXTERNAL LINKS')
    responses[wikipedia.api_url]['mcy_ds_external_links'] = res

    # doesn't contain external links
    pg = wikipedia.page('Tropical rainforest conservation')
    res = pg.parse_section_links('EXTERNAL LINKS')
    responses[wikipedia.api_url]['page_no_sec_links'] = res

    pg = asoiaf.page('arya')
    for section in pg.sections:
        links = pg.parse_section_links(section)
        responses[asoiaf.api_url]['arya_{}_links'.format(section)] = links

    print("Completed pulling the section links")

if PULL_ALL is True or PULL_TABLE_OF_CONTENTS is True:
    pg = wikipedia.page('New York City')
    res = pg.sections
    responses[wikipedia.api_url]['new_york_city_sections'] = res
    res = pg.table_of_contents
    responses[wikipedia.api_url]['new_york_city_toc'] = res
    responses[wikipedia.api_url]['new_york_city_air_quality'] = pg.section('Air quality')
    responses[wikipedia.api_url]['new_york_city_last_sec'] = pg.section('External links')
    print("Completed pulling Table of Content data")

if PULL_ALL is True or PULL_LOGIN is True:
    pg = wikipedia.login(username='badusername', password='fakepassword')
    print("Completed pulling login")


if PULL_ALL is True or PULL_ISSUE_14 is True:
    res = site.page('One Two Three... Infinity').images
    responses[wikipedia.api_url]['hidden_images'] = res

    # missing http got lumped into this issue...
    page = site.page('Minneapolis')
    responses[site.api_url]['references_without_http'] = page.references

    print("Completed pulling issue 14")

if PULL_ALL is True or PULL_ISSUE_15 is True:
    res = site.page('Rober Eryol').images
    responses[wikipedia.api_url]['infinite_loop_images'] = res
    res = site.page('List of named minor planets (numerical)').links
    responses[wikipedia.api_url]['large_continued_query'] = res
    res = wikipedia.page('B8 polytope').images
    responses[wikipedia.api_url]['large_continued_query_images'] = res

    print("Completed pulling issue 15")

if PULL_ALL is True or PULL_ISSUE_35 is True:
    try:
        site.page('Leaching')
    except DisambiguationError as ex:
        responses[wikipedia.api_url]['missing_title_disamb_dets'] = ex.details
        responses[wikipedia.api_url]['missing_title_disamb_msg'] = str(ex)

    print("Completed pulling issue 35")

if PULL_ALL is True or PULL_ISSUE_39 is True:
    res = plants.categorymembers('Plant', results=None, subcategories=False)
    responses[plants.api_url]['query-continue-find'] = res

    print("Completed pulling issue 39")

# dump data to file
with open(RESPONSES_FILE, 'w') as mock:
    json.dump(responses, mock, ensure_ascii=False, indent=1, sort_keys=True)
