"""
MediaWikiPage class module
"""
# MIT License
# Author: Tyler Barrus (barrust@gmail.com)

from __future__ import unicode_literals, absolute_import
from decimal import Decimal
import re
from collections import OrderedDict
from bs4 import BeautifulSoup, Tag
from .utilities import str_or_unicode, is_relative_url
from .exceptions import (
    MediaWikiBaseException,
    MediaWikiException,
    PageError,
    RedirectError,
    DisambiguationError,
    ODD_ERROR_MESSAGE,
)


class MediaWikiPage(object):
    """ MediaWiki Page Instance

        Args:
            mediawiki (MediaWiki): MediaWiki class object from which to pull
            title (str): Title of page to retrieve
            pageid (int): MediaWiki site pageid to retrieve
            redirect (bool): **True:** Follow redirects
            preload (bool): **True:** Load most properties after getting page
            original_title (str): Not to be used from the caller; used to \
                                  help follow redirects
        Raises:
            :py:func:`mediawiki.exceptions.PageError`: if page provided does \
            not exist
        Raises:
            :py:func:`mediawiki.exceptions.DisambiguationError`: if page \
            provided is a disambiguation page
        Raises:
            :py:func:`mediawiki.exceptions.RedirectError`: if redirect is \
            **False** and the pageid or title provided redirects to another \
            page
        Warning:
            This should never need to be used directly! Please use \
            :func:`mediawiki.MediaWiki.page` """
    __slots__ = [
        "mediawiki",
        "url",
        "title",
        "original_title",
        "pageid",
        "_content",
        "_revision_id",
        "_parent_id",
        "_html",
        "_soup",
        "_images",
        "_references",
        "_categories",
        "_coordinates",
        "_links",
        "_redirects",
        "_backlinks",
        "_langlinks",
        "_summary",
        "_sections",
        "_table_of_contents",
        "_logos",
        "_hatnotes",
    ]

    def __init__(
        self,
        mediawiki,
        title=None,
        pageid=None,
        redirect=True,
        preload=False,
        original_title="",
    ):

        self.mediawiki = mediawiki
        self.url = None
        if title is not None:
            self.title = title
            self.original_title = original_title or title
        elif pageid is not None:
            self.pageid = pageid
        else:
            raise ValueError("Either a title or a pageid must be specified")

        self._content = None
        self._revision_id = None
        self._parent_id = None
        self._html = False  # None signifies nothing returned...
        self._images = None
        self._references = None
        self._categories = None
        self._coordinates = False  # None signifies nothing returned...
        self._links = None
        self._redirects = None
        self._backlinks = None
        self._langlinks = None
        self._summary = None
        self._sections = None
        self._table_of_contents = None
        self._logos = None
        self._hatnotes = None
        self._soup = None

        self.__load(redirect=redirect, preload=preload)

        preload_props = [
            "content",
            "summary",
            "images",
            "references",
            "links",
            "sections",
            "redirects",
            "coordinates",
            "backlinks",
            "categories",
        ]
        if preload:
            for prop in preload_props:
                getattr(self, prop)
    # end __init__

    def __repr__(self):
        """ repr """
        return self.__str__()

    def __unicode__(self):
        """ python 2.7 unicode """
        return """<MediaWikiPage '{0}'>""".format(self.title)

    def __str__(self):
        """ python > 3 unicode python 2.7 byte str """
        return str_or_unicode(self.__unicode__())

    def __eq__(self, other):
        """ base eq function """
        try:
            return (
                self.pageid == other.pageid
                and self.title == other.title
                and self.url == other.url
            )
        except AttributeError:
            return False

    # Properties
    def _pull_content_revision_parent(self):
        """ combine the pulling of these three properties """

        if self._revision_id is None:
            query_params = {
                "prop": "extracts|revisions",
                "explaintext": "",
                "rvprop": "ids",
            }
            query_params.update(self.__title_query_param())
            request = self.mediawiki.wiki_request(query_params)
            page_info = request["query"]["pages"][self.pageid]
            self._content = page_info.get("extract", None)
            self._revision_id = page_info["revisions"][0]["revid"]
            self._parent_id = page_info["revisions"][0]["parentid"]

            if self._content is None and 'TextExtracts' not in self.mediawiki.extensions:
                msg = "Unable to extract page content; the TextExtracts extension must be installed!"
                raise MediaWikiBaseException(msg)
        return self._content, self._revision_id, self._parent_id

    @property
    def content(self):
        """ str: The page content in text format

            Note:
                Not settable
            Note:
                Side effect is to also get revision_id and parent_id """
        if self._content is None:
            self._pull_content_revision_parent()
        return self._content

    @property
    def revision_id(self):
        """ int: The current revision id of the page

            Note:
                Not settable
            Note:
                Side effect is to also get content and parent_id """
        if self._revision_id is None:
            self._pull_content_revision_parent()
        return self._revision_id

    @property
    def parent_id(self):
        """ int: The parent id of the page

            Note:
                Not settable
            Note:
                Side effect is to also get content and revision_id """
        if self._parent_id is None:
            self._pull_content_revision_parent()
        return self._parent_id

    @property
    def html(self):
        """ str: HTML representation of the page

            Note:
                Not settable
            Warning:
                This can be slow for very large pages """
        if self._html is False:
            self._html = None
            query_params = {
                "prop": "revisions",
                "rvprop": "content",
                "rvlimit": 1,
                "rvparse": "",
                "titles": self.title,
            }
            request = self.mediawiki.wiki_request(query_params)
            page = request["query"]["pages"][self.pageid]
            self._html = page["revisions"][0]["*"]
        return self._html

    @property
    def images(self):
        """ list: Images on the page

            Note:
                Not settable """
        if self._images is None:
            self._images = list()
            params = {
                "generator": "images",
                "gimlimit": "max",
                "prop": "imageinfo",  # this will be replaced by fileinfo
                "iiprop": "url",
            }
            for page in self._continued_query(params):
                if "imageinfo" in page and "url" in page["imageinfo"][0]:
                    self._images.append(page["imageinfo"][0]["url"])
            self._images = sorted(self._images)
        return self._images

    @property
    def logos(self):
        """ list: Parse images within the infobox signifying either the main \
                  image or logo

            Note:
                Not settable
            Note:
                Side effect is to also pull the html which can be slow
            Note:
                This is a parsing operation and not part of the standard API"""
        if self._logos is None:
            self._logos = list()
            # Cache the results of parsing the html, so that multiple calls happen much faster
            if not self._soup:
                self._soup = BeautifulSoup(self.html, "html.parser")
            info = self._soup.find("table", {"class": "infobox"})
            if info is not None:
                children = info.find_all("a", class_="image")
                for child in children:
                    self._logos.append("https:" + child.img["src"])
        return self._logos

    @property
    def hatnotes(self):
        """ list: Parse hatnotes from the HTML

            Note:
                Not settable
            Note:
                Side effect is to also pull the html which can be slow
            Note:
                This is a parsing operation and not part of the standard API"""
        if self._hatnotes is None:
            self._hatnotes = list()
            # Cache the results of parsing the html, so that multiple calls happen much faster
            if not self._soup:
                self._soup = BeautifulSoup(self.html, "html.parser")
            notes = self._soup.find_all("div", class_="hatnote")
            if notes is not None:
                for note in notes:
                    tmp = list()
                    for child in note.children:
                        if hasattr(child, "text"):
                            tmp.append(child.text)
                        else:
                            tmp.append(child)
                    self._hatnotes.append("".join(tmp))
        return self._hatnotes

    @property
    def references(self):
        """ list: External links, or references, listed anywhere on the \
                  MediaWiki page
            Note:
                Not settable
            Note
                May include external links within page that are not \
                technically cited anywhere """
        if self._references is None:
            self._references = list()
            self.__pull_combined_properties()
        return self._references

    @property
    def categories(self):
        """ list: Non-hidden categories on the page

            Note:
                Not settable """
        if self._categories is None:
            self._categories = list()
            self.__pull_combined_properties()
        return self._categories

    @property
    def coordinates(self):
        """ Tuple: GeoCoordinates of the place referenced; results in \
            lat/long tuple or None if no geocoordinates present

            Note:
                Not settable
            Note:
                Requires the GeoData extension to be installed """
        if self._coordinates is False:
            self._coordinates = None
            self.__pull_combined_properties()
        return self._coordinates

    @property
    def links(self):
        """ list: List of all MediaWiki page links on the page

            Note:
                Not settable """
        if self._links is None:
            self._links = list()
            self.__pull_combined_properties()
        return self._links

    @property
    def redirects(self):
        """ list: List of all redirects to this page; **i.e.,** the titles \
            listed here will redirect to this page title

            Note:
                Not settable """
        if self._redirects is None:
            self._redirects = list()
            self.__pull_combined_properties()
        return self._redirects

    @property
    def backlinks(self):
        """ list: Pages that link to this page

            Note:
                Not settable """
        if self._backlinks is None:
            self._backlinks = list()
            params = {
                "action": "query",
                "list": "backlinks",
                "bltitle": self.title,
                "bllimit": "max",
                "blfilterredir": "nonredirects",
                "blnamespace": 0,
            }
            tmp = [link["title"] for link in self._continued_query(params, "backlinks")]
            self._backlinks = sorted(tmp)
        return self._backlinks

    @property
    def langlinks(self):
        """ dict: Names of the page in other languages for which page is \
            where the key is the language code and the page name is the name \
            of the page in that language.

        Note:
            Not settable
        Note:
            list of all language links from the provided pages to other \
            languages according to: \
            https://www.mediawiki.org/wiki/API:Langlinks """

        if self._langlinks is None:
            params = {"prop": "langlinks", "cllimit": "max"}
            query_result = self._continued_query(params)

            langlinks = dict()
            for lang_info in query_result:
                langlinks[lang_info["lang"]] = lang_info["*"]
            self._langlinks = langlinks
        return self._langlinks

    @property
    def summary(self):
        """ str: Default page summary

            Note:
                Not settable """
        if self._summary is None:
            self.__pull_combined_properties()
        return self._summary

    def summarize(self, sentences=0, chars=0):
        """ Summarize page either by number of sentences, chars, or first
            section (**default**)

            Args:
                sentences (int): Number of sentences to use in summary \
                                 (first `x` sentences)
                chars (int): Number of characters to use in summary \
                             (first `x` characters)
            Returns:
                str: The summary of the MediaWiki page
            Note:
                Precedence for parameters: sentences then chars; if both are \
                0 then the entire first section is returned """
        query_params = {"prop": "extracts", "explaintext": "", "titles": self.title}
        if sentences:
            query_params["exsentences"] = 10 if sentences > 10 else sentences
        elif chars:
            query_params["exchars"] = 1 if chars < 1 else chars
        else:
            query_params["exintro"] = ""

        request = self.mediawiki.wiki_request(query_params)
        summary = request["query"]["pages"][self.pageid].get("extract")
        return summary

    @property
    def sections(self):
        """ list: Table of contents sections

            Note:
                Not settable """
        # NOTE: Due to MediaWiki sites adding superscripts or italics or bold
        #       information in the sections, moving to regex to get the
        #       `non-decorated` name instead of using the query api!
        if self._sections is None:
            self._parse_sections()
        return self._sections

    @property
    def table_of_contents(self):
        """ OrderedDict: Dictionary of sections and sub-sections

            Note:
                Leaf nodes are empty OrderedDict objects
            Note:
                Not Settable"""

        if self._table_of_contents is None:
            self._parse_sections()
        return self._table_of_contents

    def section(self, section_title):
        """ Plain text section content

            Args:
                section_title (str): Name of the section to pull
            Returns:
                str: The content of the section
            Note:
                Returns **None** if section title is not found; only text \
                between title and next section or sub-section title is returned
            Note:
                Side effect is to also pull the content which can be slow
            Note:
                This is a parsing operation and not part of the standard API"""
        section = "== {0} ==".format(section_title)
        try:
            content = self.content
            index = content.index(section) + len(section)

            # ensure we have the full section header...
            while True:
                if content[index + 1] == "=":
                    index += 1
                else:
                    break
        except ValueError:
            return None
        except IndexError:
            pass

        try:
            next_index = self.content.index("==", index)
        except ValueError:
            next_index = len(self.content)

        return self.content[index:next_index].lstrip("=").strip()

    def parse_section_links(self, section_title):
        """ Parse all links within a section

            Args:
                section_title (str): Name of the section to pull
            Returns:
                list: List of (title, url) tuples
            Note:
                Returns **None** if section title is not found
            Note:
                Side effect is to also pull the html which can be slow
            Note:
                This is a parsing operation and not part of the standard API"""
        # Cache the results of parsing the html, so that multiple calls happen much faster
        if not self._soup:
            self._soup = BeautifulSoup(self.html, "html.parser")

        headlines = self._soup.find_all("span", class_="mw-headline")
        tmp_soup = BeautifulSoup(section_title, "html.parser")
        tmp_sec_title = tmp_soup.get_text().lower()
        id_tag = None
        for headline in headlines:
            tmp_id = headline.text
            if tmp_id.lower() == tmp_sec_title:
                id_tag = headline.get("id")
                break

        if id_tag is not None:
            return self._parse_section_links(id_tag)
        return None

    # Protected Methods
    def __load(self, redirect=True, preload=False):
        """ load the basic page information """
        query_params = {
            "prop": "info|pageprops",
            "inprop": "url",
            "ppprop": "disambiguation",
            "redirects": "",
        }
        query_params.update(self.__title_query_param())

        request = self.mediawiki.wiki_request(query_params)

        query = request["query"]
        pageid = list(query["pages"].keys())[0]
        page = query["pages"][pageid]

        # determine result of the request
        # missing is present if the page is missing
        if "missing" in page:
            self._raise_page_error()
        # redirects is present in query if page is a redirect
        elif "redirects" in query:
            self._handle_redirect(redirect, preload, query, page)
        # if pageprops is returned, it must be a disambiguation error
        elif "pageprops" in page:
            self._raise_disambiguation_error(page, pageid)
        else:
            self.pageid = pageid
            self.title = page["title"]
            self.url = page["fullurl"]

    def _raise_page_error(self):
        """ raise the correct type of page error """
        if hasattr(self, "title"):
            raise PageError(title=self.title)
        raise PageError(pageid=self.pageid)

    def _raise_disambiguation_error(self, page, pageid):
        """ parse and throw a disambiguation error """
        query_params = {
            "prop": "revisions",
            "rvprop": "content",
            "rvparse": "",
            "rvlimit": 1,
        }
        query_params.update(self.__title_query_param())
        request = self.mediawiki.wiki_request(query_params)
        html = request["query"]["pages"][pageid]["revisions"][0]["*"]

        lis = BeautifulSoup(html, "html.parser").find_all("li")
        filtered_lis = [
            li for li in lis if "tocsection" not in "".join(li.get("class", list()))
        ]
        may_refer_to = [li.a.get_text() for li in filtered_lis if li.a]

        disambiguation = list()
        for lis_item in filtered_lis:
            item = lis_item.find_all("a")
            one_disambiguation = dict()
            one_disambiguation["description"] = lis_item.text
            if item and item[0].has_attr("title"):
                one_disambiguation["title"] = item[0]["title"]
            else:
                # these are non-linked records so double up the text
                one_disambiguation["title"] = lis_item.text
            disambiguation.append(one_disambiguation)
        raise DisambiguationError(
            getattr(self, "title", page["title"]),
            may_refer_to,
            page["fullurl"],
            disambiguation,
        )

    def _handle_redirect(self, redirect, preload, query, page):
        """ handle redirect """
        if redirect:
            redirects = query["redirects"][0]

            if "normalized" in query:
                normalized = query["normalized"][0]
                if normalized["from"] != self.title:
                    raise MediaWikiException(ODD_ERROR_MESSAGE)
                from_title = normalized["to"]
            else:
                if not getattr(self, "title", None):
                    self.title = redirects["from"]
                    delattr(self, "pageid")
                from_title = self.title
            if redirects["from"] != from_title:
                raise MediaWikiException(ODD_ERROR_MESSAGE)

            # change the title and reload the whole object
            self.__init__(
                self.mediawiki,
                title=redirects["to"],
                redirect=redirect,
                preload=preload,
            )
        else:
            raise RedirectError(getattr(self, "title", page["title"]))

    def _continued_query(self, query_params, key="pages"):
        """ Based on
            https://www.mediawiki.org/wiki/API:Query#Continuing_queries """
        query_params.update(self.__title_query_param())

        last_cont = dict()
        prop = query_params.get("prop")

        while True:
            params = query_params.copy()
            params.update(last_cont)

            request = self.mediawiki.wiki_request(params)

            if "query" not in request:
                break

            pages = request["query"][key]
            if "generator" in query_params:
                for datum in pages.values():
                    yield datum
            elif isinstance(pages, list):
                for datum in list(enumerate(pages)):
                    yield datum[1]
            else:
                for datum in pages[self.pageid].get(prop, list()):
                    yield datum

            if "continue" not in request or request["continue"] == last_cont:
                break

            last_cont = request["continue"]

    def _parse_section_links(self, id_tag):
        """ given a section id, parse the links in the unordered list """

        info = self._soup.find("span", {"id": id_tag})
        all_links = list()

        if info is None:
            return all_links

        for node in self._soup.find(id=id_tag).parent.next_siblings:
            if not isinstance(node, Tag):
                continue
            if node.get("role", "") == "navigation":
                continue
            elif "infobox" in node.get("class", []):
                continue

            # this is actually the child node's class...
            is_headline = node.find("span", {"class": "mw-headline"})
            if is_headline is not None:
                break
            if node.name == "a":
                all_links.append(self.__parse_link_info(node))
            else:
                for link in node.find_all("a"):
                    all_links.append(self.__parse_link_info(link))
        return all_links

    def __parse_link_info(self, link):
        """ parse the <a> tag for the link """
        href = link.get("href", "")
        txt = link.string or href
        is_rel = is_relative_url(href)
        if is_rel is True:
            tmp = "{0}{1}".format(self.mediawiki.base_url, href)
        elif is_rel is None:
            tmp = "{0}{1}".format(self.url, href)
        else:
            tmp = href
        return txt, tmp

    def _parse_sections(self):
        """ parse sections and TOC """

        def _list_to_dict(_dict, path, sec):
            tmp = _dict
            for elm in path[:-1]:
                tmp = tmp[elm]
            tmp[sec] = OrderedDict()

        self._sections = list()
        section_regexp = r"\n==* .* ==*\n"  # '== {STUFF_NOT_\n} =='
        found_obj = re.findall(section_regexp, self.content)

        res = OrderedDict()
        path = list()
        last_depth = 0
        for obj in found_obj:
            depth = obj.count("=") / 2  # this gets us to the single side...
            depth -= 2  # now, we can calculate depth

            sec = obj.lstrip("\n= ").rstrip(" =\n")
            if depth == 0:
                last_depth = 0
                path = [sec]
                res[sec] = OrderedDict()
            elif depth > last_depth:
                last_depth = depth
                path.append(sec)
                _list_to_dict(res, path, sec)
            elif depth < last_depth:
                # path.pop()
                while last_depth > depth:
                    path.pop()
                    last_depth -= 1
                path.pop()
                path.append(sec)
                _list_to_dict(res, path, sec)
                last_depth = depth
            else:
                path.pop()
                path.append(sec)
                _list_to_dict(res, path, sec)
                last_depth = depth
            self._sections.append(sec)

        self._table_of_contents = res

    def __title_query_param(self):
        """ util function to determine which parameter method to use """
        if getattr(self, "title", None) is not None:
            return {"titles": self.title}
        return {"pageids": self.pageid}

    def __pull_combined_properties(self):
        """ something here... """

        query_params = {
            "titles": self.title,
            "prop": "extracts|redirects|links|coordinates|categories|extlinks",
            "continue": dict(),
            # summary
            "explaintext": "",
            "exintro": "",  # full first section for the summary!
            # redirects
            "rdprop": "title",
            "rdlimit": "max",
            # links
            "plnamespace": 0,
            "pllimit": "max",
            # coordinates
            "colimit": "max",
            # categories
            "cllimit": "max",
            "clshow": "!hidden",
            # references
            "ellimit": "max",
        }

        last_cont = dict()
        results = dict()
        idx = 0
        while True:
            params = query_params.copy()
            params.update(last_cont)

            request = self.mediawiki.wiki_request(params)
            idx += 1

            if "query" not in request:
                break

            keys = [
                "extracts",
                "redirects",
                "links",
                "coordinates",
                "categories",
                "extlinks",
            ]
            new_cont = request.get("continue")
            request = request["query"]["pages"][self.pageid]
            if not results:
                results = request
            else:
                for key in keys:
                    if key in request and request.get(key) is not None:
                        val = request.get(key)
                        tmp = results.get(key)
                        if isinstance(tmp, (list, tuple)):
                            results[key] = results.get(key, list) + val
            if new_cont is None or new_cont == last_cont:
                break

            last_cont = new_cont

        # redirects
        tmp = [link["title"] for link in results.get("redirects", list())]
        self._redirects = sorted(tmp)

        # summary
        self._summary = results.get("extract")

        # links
        tmp = [link["title"] for link in results.get("links", list())]
        self._links = sorted(tmp)

        # categories
        def _get_cat(val):
            """ parse the category correctly """
            tmp = val["title"]
            if tmp.startswith(self.mediawiki.category_prefix):
                return tmp[len(self.mediawiki.category_prefix) + 1:]
            return tmp

        tmp = [_get_cat(link) for link in results.get("categories", list())]
        self._categories = sorted(tmp)

        # coordinates
        if "coordinates" in results:
            self._coordinates = (
                Decimal(results["coordinates"][0]["lat"]),
                Decimal(results["coordinates"][0]["lon"]),
            )

        # references
        tmp = [link["*"] for link in results.get("extlinks", list())]
        self._references = sorted(tmp)
