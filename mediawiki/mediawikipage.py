'''
MediaWikiPage class module
'''
# MIT License
# Author: Tyler Barrus (barrust@gmail.com)

from __future__ import (unicode_literals, absolute_import)
from decimal import (Decimal)
from bs4 import (BeautifulSoup, Tag)
from .utilities import (str_or_unicode, is_relative_url)
from .exceptions import (MediaWikiException, PageError, RedirectError,
                         DisambiguationError, ODD_ERROR_MESSAGE)


class MediaWikiPage(object):
    '''
    MediaWiki Page Instance

    :param mediawiki: MediWiki class object from which to pull information
    :type mediawiki: MediaWiki class object
    :param title: Title of page to retrieve
    :type title: string or None
    :param pageid: MediaWiki site pageid to retrieve
    :type pageid: integer or None
    :param redirect: **True:** Follow redirects
    :type redirect: Boolean
    :param preload: **True:** Load most properties after getting page
    :type preload: Boolean
    :param original_title: Not to be used from the caller; used to help \
    follow redirects
    :type original_title: String

    :raises `mediawiki.exceptions.PageError`: if page provided does not exist
    :raises `mediawiki.exceptions.DisambiguationError`: if page provided \
    is a disambiguation page
    :raises `mediawiki.exceptions.RedirectError`: if redirect is **False** \
    and the pageid or title provided redirects to another page

    .. warning:: This should never need to be used directly! Please use \
    :func:`mediawiki.MediaWiki.page`
    '''

    def __init__(self, mediawiki, title=None, pageid=None, redirect=True,
                 preload=False, original_title=''):

        self.mediawiki = mediawiki
        self.url = None
        if title is not None:
            self.title = title
            self.original_title = original_title or title
        elif pageid is not None:
            self.pageid = pageid
        else:
            raise ValueError('Either a title or a pageid must be specified')

        self._content = ''
        self._revision_id = False
        self._parent_id = False
        self._html = False
        self._images = False
        self._references = False
        self._categories = False
        self._coordinates = False
        self._links = False
        self._redirects = False
        self._backlinks = False
        self._summary = False
        self._sections = False
        self._logos = False
        self._hatnotes = False

        self.__load(redirect=redirect, preload=preload)

        preload_props = ['content', 'summary', 'images', 'references', 'links',
                         'sections', 'redirects', 'coordinates', 'backlinks',
                         'categories']
        if preload:
            for prop in preload_props:
                getattr(self, prop)
        # end __init__

    def __repr__(self):
        ''' repr '''
        return self.__str__()

    def __unicode__(self):
        ''' python 2.7 unicode '''
        return '''<MediaWikiPage '{0}'>'''.format(self.title)

    def __str__(self):
        ''' python > 3 unicode python 2.7 byte str '''
        return str_or_unicode(self.__unicode__())

    def __eq__(self, other):
        ''' base eq function '''
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

        if self._revision_id is False:
            query_params = {
                'prop': 'extracts|revisions',
                'explaintext': '',
                'rvprop': 'ids'
            }
            query_params.update(self.__title_query_param())
            request = self.mediawiki.wiki_request(query_params)
            page_info = request['query']['pages'][self.pageid]
            self._content = page_info['extract']
            self._revision_id = page_info['revisions'][0]['revid']
            self._parent_id = page_info['revisions'][0]['parentid']
        return self._content, self._revision_id, self._parent_id

    @property
    def content(self):
        ''' Page content

        :getter: Returns the page content
        :setter: Not settable
        :type: string

        .. note:: Side effect is to also get revision_id and parent_id
        '''
        if self._content is '':
            self._pull_content_revision_parent()
        return self._content

    @property
    def revision_id(self):
        ''' Current revision id

        :getter: Returns the current revision id of the page
        :setter: Not settable
        :type: integer

        .. note:: Side effect is to also get content and parent_id
        '''
        if self._revision_id is False:
            self._pull_content_revision_parent()
        return self._revision_id

    @property
    def parent_id(self):
        ''' Current parent id

        :getter: Returns the parent id of the page
        :setter: Not settable
        :type: integer

        .. note:: Side effect is to also get content and revision_id
        '''
        if self._parent_id is False:
            self._pull_content_revision_parent()
        return self._parent_id

    @property
    def html(self):
        ''' Page HTML

        :getter: Returns the HTML of the page
        :setter: Not settable
        :type: string

        .. warning:: This can be slow for very large pages
        '''
        if self._html is False:
            self._html = None
            query_params = {
                'prop': 'revisions',
                'rvprop': 'content',
                'rvlimit': 1,
                'rvparse': '',
                'titles': self.title
            }
            request = self.mediawiki.wiki_request(query_params)
            page = request['query']['pages'][self.pageid]
            self._html = page['revisions'][0]['*']
        return self._html

    @property
    def images(self):
        ''' Images on the page

        :getter: Returns the list of all image URLs on the page
        :setter: Not settable
        :type: list
        '''
        if self._images is False:
            self._images = list()
            params = {
                'generator': 'images',
                'gimlimit': 'max',
                'prop': 'imageinfo',  # this will be replaced by fileinfo
                'iiprop': 'url'
            }
            for page in self._continued_query(params):
                if 'imageinfo' in page and 'url' in page['imageinfo'][0]:
                    self._images.append(page['imageinfo'][0]['url'])
            self._images = sorted(self._images)
        return self._images

    @property
    def logos(self):
        ''' Parse images within the infobox signifying either the main image \
        or logo

        :getter: Returns the list of all images in the information box
        :setter: Not settable
        :type: list

        .. note:: Side effect is to also pull the html which can be slow
        .. note:: This is a parsing operation and not part of the standard API
        '''
        if self._logos is False:
            self._logos = list()
            soup = BeautifulSoup(self.html, 'html.parser')
            info = soup.find('table', {'class': 'infobox'})
            if info is not None:
                children = info.findAll('', {'class': 'image'})
                for child in children:
                    self._logos.append('https:' + child.img['src'])
        return self._logos

    @property
    def hatnotes(self):
        ''' Parse hatnotes from the html

        :getter: Returns the list of all hatnotes from the page
        :setter: Not settable
        :type: list

        .. note:: Side effect is to also pull the html which can be slow
        .. note:: This is a parsing operation and not part of the standard API
        '''
        if self._hatnotes is False:
            self._hatnotes = list()
            soup = BeautifulSoup(self.html, 'html.parser')
            notes = soup.findAll('', {'class': 'hatnote'})
            if notes is not None:
                for note in notes:
                    tmp = list()
                    for child in note.children:
                        if hasattr(child, 'text'):
                            tmp.append(child.text)
                        else:
                            tmp.append(child)
                    self._hatnotes.append(''.join(tmp))
        return self._hatnotes

    @property
    def references(self):
        ''' External links, or references, listed anywhere on the MediaWiki \
            page

        :getter: Returns the list of all external links
        :setter: Not settable
        :type: list

        .. note:: May include external links within page that are not \
        technically cited anywhere.
        '''
        if self._references is False:
            params = {'prop': 'extlinks', 'ellimit': 'max'}
            tmp = [link['*'] for link in self._continued_query(params)]
            self._references = sorted(tmp)
        return self._references

    @property
    def categories(self):
        ''' Non-hidden categories on the page

        :getter: Returns the list of all non-hidden categories on the page
        :setter: Not settable
        :type: list
        '''
        if self._categories is False:

            def _get_cat(val):
                ''' parse the category correctly '''
                tmp = val['title']
                if tmp.startswith('Category:'):
                    return tmp[9:]
                return tmp

            params = {
                'prop': 'categories',
                'cllimit': 'max',
                'clshow': '!hidden'
            }
            tmp = [_get_cat(link) for link in self._continued_query(params)]
            self._categories = sorted(tmp)
        return self._categories

    @property
    def coordinates(self):
        ''' GeoCoordinates of the place referenced

        :getter: Returns the geocoordinates of the place that the page \
        references
        :setter: Not settable
        :type: Tuple (Latitude, Logitude) or None if no geocoordinates present

        .. note: Requires the GeoData extension to be installed
        '''
        if self._coordinates is False:
            self._coordinates = None
            params = {
                'prop': 'coordinates',
                'colimit': 'max',
                'titles': self.title
            }
            request = self.mediawiki.wiki_request(params)
            res = request['query']['pages'][self.pageid]
            if 'query' in request and 'coordinates' in res:
                self._coordinates = (Decimal(res['coordinates'][0]['lat']),
                                     Decimal(res['coordinates'][0]['lon']))
        return self._coordinates

    @property
    def links(self):
        ''' MediaWiki page links on a page

        :getter: Returns the list of all MediaWiki page links on this page
        :setter: Not settable
        :type: list
        '''
        if self._links is False:
            self._links = list()
            params = {
                'prop': 'links',
                'plnamespace': 0,
                'pllimit': 'max'
            }
            tmp = [link['title'] for link in self._continued_query(params)]
            self._links = sorted(tmp)
        return self._links

    @property
    def redirects(self):
        ''' Redirects to the page

        :getter: Returns the list of all redirects to this page; \
        **i.e.,** the titles listed here will redirect to this page title
        :setter: Not settable
        :type: list
        '''
        if self._redirects is False:
            self._redirects = list()
            params = {
                'prop': 'redirects',
                'rdprop': 'title',
                'rdlimit': 'max'
            }
            tmp = [link['title'] for link in self._continued_query(params)]
            self._redirects = sorted(tmp)
        return self._redirects

    @property
    def backlinks(self):
        ''' Pages that link to this page

        :getter: Returns the list of all pages that link to this page
        :setter: Not settable
        :type: list
        '''
        if self._backlinks is False:
            self._backlinks = list()
            params = {
                'action': 'query',
                'list': 'backlinks',
                'bltitle': self.title,
                'bllimit': 'max',
                'blfilterredir': 'nonredirects',
                'blnamespace': 0
            }
            tmp = [link['title']
                   for link in self._continued_query(params, 'backlinks')]
            self._backlinks = sorted(tmp)
        return self._backlinks

    @property
    def summary(self):
        ''' Default page summary

        :getter: Returns the first section of the MediaWiki page
        :setter: Not settable
        :type: string
        '''
        if self._summary is False:
            self._summary = self.summarize()
        return self._summary

    def summarize(self, sentences=0, chars=0):
        ''' Summarize page either by number of sentences, chars, or first
        section (**default**)

        :param sentences: Number of sentences to use in summary \
        (first `x` sentences)
        :type sentences: integer
        :param chars: Number of characters to use in summary \
        (first `x` characters)
        :type chars: integer
        :returns: string

        .. note:: Precedence for parameters: sentences then chars; \
        if both are 0 then the entire first section is returned
        '''
        query_params = {
            'prop': 'extracts',
            'explaintext': '',
            'titles': self.title
        }
        if sentences:
            query_params['exsentences'] = (10 if sentences > 10 else sentences)
        elif chars:
            query_params['exchars'] = (1 if chars < 1 else chars)
        else:
            query_params['exintro'] = ''

        request = self.mediawiki.wiki_request(query_params)
        summary = request['query']['pages'][self.pageid]['extract']
        return summary

    @property
    def sections(self):
        ''' Table of contents sections

        :getter: Returns the sections listed in the table of contents
        :setter: Not settable
        :type: list
        '''
        if self._sections is False:
            query_params = {'action': 'parse', 'prop': 'sections'}
            if not getattr(self, 'title', None):
                query_params['pageid'] = self.pageid
            else:
                query_params['page'] = self.title
            request = self.mediawiki.wiki_request(query_params)
            sections = request['parse']['sections']
            self._sections = [section['line'] for section in sections]

        return self._sections

    def section(self, section_title):
        ''' Plain text section content

        :param section_title: Name of the section to pull
        :type section_title: string
        :returns: string or None if section title is not found

        .. note:: Returns **None** if section title is not found; \
        only text between title and next section or sub-section title \
        is returned.
        .. note:: Side effect is to also pull the content which can be slow
        .. note:: This is a parsing operation and not part of the standard API
        '''
        section = '== {0} =='.format(section_title)
        try:
            content = self.content
            index = content.index(section) + len(section)
        except ValueError:
            return None

        try:
            next_index = self.content.index('==', index)
        except ValueError:
            next_index = len(self.content)

        return self.content[index:next_index].lstrip('=').strip()

    def parse_section_links(self, section_title):
        ''' Parse all links within a section

        :param section_title: Name of the section to pull
        :typee section_title: string
        :return: list of (title, url) tuples

        .. note:: Returns **None** if section title is not found
        .. note:: Side effect is to also pull the html which can be slow
        .. note:: This is a parsing operation and not part of the standard API
        '''
        soup = BeautifulSoup(self.html, 'html.parser')
        headlines = soup.find_all('span', {'class': 'mw-headline'})
        tmp_soup = BeautifulSoup(section_title, 'html.parser')
        tmp_sec_title = tmp_soup.get_text().lower()
        id_tag = None
        for headline in headlines:
            tmp_id = headline.text
            if tmp_id.lower() == tmp_sec_title:
                id_tag = headline.get('id')
                break

        if id_tag is not None:
            return self._parse_section_links(id_tag)
        return None

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

        request = self.mediawiki.wiki_request(query_params)

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
        request = self.mediawiki.wiki_request(query_params)
        html = request['query']['pages'][pageid]['revisions'][0]['*']

        lis = BeautifulSoup(html, 'html.parser').find_all('li')
        filtered_lis = [li for li in lis if 'tocsection' not in
                        ''.join(li.get('class', list()))]
        may_refer_to = [li.a.get_text() for li in filtered_lis if li.a]

        disambiguation = list()
        for lis_item in filtered_lis:
            item = lis_item.find_all('a')
            one_disambiguation = dict()
            one_disambiguation['description'] = lis_item.text
            if item and hasattr(item, 'title'):
                one_disambiguation['title'] = item[0]['title']
            else:
                # these are non-linked records so double up the text
                one_disambiguation['title'] = lis_item.text
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
                if normalized['from'] != self.title:
                    raise MediaWikiException(ODD_ERROR_MESSAGE)
                from_title = normalized['to']
            else:
                if not getattr(self, 'title', None):
                    self.title = redirects['from']
                    delattr(self, 'pageid')
                from_title = self.title
            if redirects['from'] != from_title:
                raise MediaWikiException(ODD_ERROR_MESSAGE)

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

        last_cont = dict()
        prop = query_params.get('prop')

        while True:
            params = query_params.copy()
            params.update(last_cont)

            request = self.mediawiki.wiki_request(params)

            if 'query' not in request:
                break

            pages = request['query'][key]
            if 'generator' in query_params:
                for datum in pages.values():
                    yield datum
            elif isinstance(pages, list):
                for datum in list(enumerate(pages)):
                    yield datum[1]
            else:
                for datum in pages[self.pageid].get(prop, list()):
                    yield datum

            if 'continue' not in request or request['continue'] == last_cont:
                break

            last_cont = request['continue']
    # end _continued_query

    def _parse_section_links(self, id_tag):
        ''' given a section id, parse the links in the unordered list '''
        soup = BeautifulSoup(self.html, 'html.parser')
        info = soup.find('span', {'id': id_tag})
        all_links = list()

        if info is None:
            return all_links

        for node in soup.find(id=id_tag).parent.next_siblings:
            if not isinstance(node, Tag):
                continue
            elif node.get('role', '') == 'navigation':
                continue
            elif 'infobox' in node.get('class', []):
                continue

            # this is actually the child node's class...
            is_headline = node.find('span', {'class': 'mw-headline'})
            if is_headline is not None:
                break
            elif node.name == 'a':
                all_links.append(self.__parse_link_info(node))
            else:
                for link in node.findAll('a'):
                    all_links.append(self.__parse_link_info(link))
        return all_links
    # end _parse_section_links

    def __parse_link_info(self, link):
        ''' parse the <a> tag for the link '''
        href = link.get('href', '')
        txt = link.string or href
        is_rel = is_relative_url(href)
        if is_rel is True:
            tmp = '{0}{1}'.format(self.mediawiki.base_url, href)
        elif is_rel is None:
            tmp = '{0}{1}'.format(self.url, href)
        else:
            tmp = href
        return txt, tmp
    # end __parse_link_info

    def __title_query_param(self):
        ''' util function to determine which parameter method to use '''
        if getattr(self, 'title', None) is not None:
            return {'titles': self.title}
        else:
            return {'pageids': self.pageid}
    # end __title_query_param

# end MediaWikiPage Class
