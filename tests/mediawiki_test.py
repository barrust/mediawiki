import unittest

import sys
sys.dont_write_bytecode = True

from mediawiki import MediaWiki



class MediaWikiOverloaded(MediaWiki):
    def __init__(self):
        MediaWiki.__init__(self)

    def _get_site_info(self):
        self._api_version = (1,28,0,)  # current wikipedia version
        self._extensions = set(['TextExtracts', 'GeoData'])


class TestMediaWiki(unittest.TestCase):

    def test_api_url(self):
        ''' test the original api '''
        site = MediaWikiOverloaded()
        self.assertEqual(site.api_url,'http://en.wikipedia.org/w/api.php')

    def test_change_lang(self):
        ''' test changing the language '''
        site = MediaWikiOverloaded()
        site.language = 'FR'
        self.assertEqual(site.language, 'fr')
        self.assertEqual(site.api_url,'http://fr.wikipedia.org/w/api.php')

    def test_api_version(self):
        site = MediaWikiOverloaded()
        self.assertEqual(site.api_version, '1.28.0')

    def test_extensions(self):
        site = MediaWikiOverloaded()
        self.assertEqual(site.extensions, set(['GeoData', 'TextExtracts']))
