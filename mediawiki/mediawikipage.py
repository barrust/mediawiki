"""
MediaWikiPage class module
"""

# MIT License
# Author: Tyler Barrus (barrust@gmail.com)

import re
from collections import OrderedDict
from decimal import Decimal
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from bs4 import BeautifulSoup, NavigableString, Tag

from mediawiki.exceptions import (
    ODD_ERROR_MESSAGE,
    DisambiguationError,
    MediaWikiBaseException,
    MediaWikiException,
    PageError,
    RedirectError,
)
from mediawiki.utilities import is_relative_url, str_or_unicode


class MediaWikiPage:
    """MediaWiki Page Instance

    Args:
        mediawiki (MediaWiki): MediaWiki class object from which to pull
        title (str): Title of page to retrieve
        pageid (int): MediaWiki site pageid to retrieve
        redirect (bool): **True:** Follow redirects
        preload (bool): **True:** Load most properties after getting page
        original_title (str): Not to be used from the caller; used to help follow redirects
    Raises:
        :py:func:`mediawiki.exceptions.PageError`: if page provided does not exist
    Raises:
        :py:func:`mediawiki.exceptions.DisambiguationError`: if page provided is a disambiguation page
    Raises:
        :py:func:`mediawiki.exceptions.RedirectError`: if redirect is **False** and the pageid or title \
            provided redirects to another page
    Warning:
        This should never need to be used directly! Please use :func:`mediawiki.MediaWiki.page`"""

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
        "_wikitext",
        "_preview",
    ]

    def __init__(
        self,
        mediawiki,
        title: Optional[str] = None,
        pageid: Optional[int] = None,
        redirect: bool = True,
        preload: bool = False,
        original_title: str = "",
    ):
        self.mediawiki = mediawiki
        self.url: Optional[str] = None
        if title is not None:
            self.title = title
            self.original_title = original_title or title
        elif pageid is not None:
            self.pageid = pageid
        else:
            raise ValueError("Either a title or a pageid must be specified")

        self._content: Optional[str] = None
        self._revision_id: Optional[int] = None
        self._parent_id: Optional[int] = None
        self._html: Union[bool, str] = False  # None signifies nothing returned...
        self._images: Optional[List[str]] = None
        self._references: Optional[List[str]] = None
        self._categories: Optional[List[str]] = None
        self._coordinates: Union[bool, None, Tuple[Decimal, Decimal]] = False  # None signifies nothing returned...
        self._links: Optional[List[str]] = None
        self._redirects: Optional[List[str]] = None
        self._backlinks: Optional[List[str]] = None
        self._langlinks: Optional[Dict[str, str]] = None
        self._summary: Optional[str] = None
        self._sections: Optional[List[str]] = None
        self._table_of_contents: Optional[Dict[str, Any]] = None
        self._logos: Optional[List[str]] = None
        self._hatnotes: Optional[List[str]] = None
        self._soup: Optional[BeautifulSoup] = None
        self._wikitext: Optional[str] = None
        self._preview: Optional[Dict[str, str]] = None

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
        """repr"""
        return self.__str__()

    def __unicode__(self):
        """python 2.7 unicode"""
        return f"""<MediaWikiPage '{self.title}'>"""

    def __str__(self):
        """python > 3 unicode python 2.7 byte str"""
        return str_or_unicode(self.__unicode__())

    def __eq__(self, other):
        """base eq function"""
        try:
            return self.pageid == other.pageid and self.title == other.title and self.url == other.url
        except AttributeError:
            return False

    # Properties
    def _pull_content_revision_parent(self) -> Tuple[Optional[str], Optional[int], Optional[int]]:
        """combine the pulling of these three properties"""

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

            if self._content is None and "TextExtracts" not in self.mediawiki.extensions:
                msg = "Unable to extract page content; the TextExtracts extension must be installed!"
                raise MediaWikiBaseException(msg)
        return self._content, self._revision_id, self._parent_id

    @property
    def content(self) -> str:
        """str: The page content in text format

        Note:
            Not settable
        Note:
            Side effect is to also get revision_id and parent_id"""
        if self._content is None:
            self._pull_content_revision_parent()
        return self._content  # type: ignore

    @property
    def revision_id(self) -> int:
        """int: The current revision id of the page

        Note:
            Not settable
        Note:
            Side effect is to also get content and parent_id"""
        if self._revision_id is None:
            self._pull_content_revision_parent()
        return self._revision_id  # type: ignore

    @property
    def parent_id(self) -> int:
        """int: The parent id of the page

        Note:
            Not settable
        Note:
            Side effect is to also get content and revision_id"""
        if self._parent_id is None:
            self._pull_content_revision_parent()
        return self._parent_id  # type: ignore

    @property
    def html(self) -> str:
        """str: HTML representation of the page

        Note:
            Not settable
        Warning:
            This can be slow for very large pages"""
        if self._html is False:
            self._html = ""
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
        return self._html  # type: ignore

    @property
    def wikitext(self) -> str:
        """str: Wikitext representation of the page

        Note:
            Not settable"""
        if self._wikitext is None:
            query_params = {
                "action": "parse",
                "pageid": self.pageid,
                "prop": "wikitext",
                "formatversion": "latest",
            }
            request = self.mediawiki.wiki_request(query_params)
            self._wikitext = request["parse"]["wikitext"]
        return self._wikitext

    @property
    def images(self) -> List[str]:
        """list: Images on the page

        Note:
            Not settable"""
        if self._images is None:
            params = {
                "generator": "images",
                "gimlimit": "max",
                "prop": "imageinfo",  # this will be replaced by fileinfo
                "iiprop": "url",
            }
            self._images = [
                page["imageinfo"][0]["url"]
                for page in self._continued_query(params)
                if "imageinfo" in page and "url" in page["imageinfo"][0]
            ]
            self._images = sorted(self._images)
        return self._images

    @property
    def logos(self) -> List[str]:
        """list: Parse images within the infobox signifying either the main image or logo

        Note:
            Not settable
        Note:
            Side effect is to also pull the html which can be slow
        Note:
            This is a parsing operation and not part of the standard API"""
        if self._logos is None:
            self._logos = []
            # Cache the results of parsing the html, so that multiple calls happen much faster
            if not self._soup:
                self._soup = BeautifulSoup(self.html, "html.parser")
            info = self._soup.find("table", {"class": "infobox"})
            if info is not None and isinstance(info, Tag):
                children = info.find_all("a", class_="image")
                self._logos.extend("https:" + child.img["src"] for child in children)
        return self._logos

    @property
    def hatnotes(self) -> List[str]:
        """list: Parse hatnotes from the HTML

        Note:
            Not settable
        Note:
            Side effect is to also pull the html which can be slow
        Note:
            This is a parsing operation and not part of the standard API"""
        if self._hatnotes is None:
            self._hatnotes = []
            # Cache the results of parsing the html, so that multiple calls happen much faster
            if not self._soup:
                self._soup = BeautifulSoup(self.html, "html.parser")
            notes = self._soup.find_all("div", class_="hatnote")
            if notes is not None:
                for note in notes:
                    tmp = []
                    for child in note.children:
                        if hasattr(child, "text"):
                            tmp.append(child.text)
                        else:
                            tmp.append(child)
                    self._hatnotes.append("".join(tmp))
        return self._hatnotes

    @property
    def references(self) -> List[str]:
        """list: External links, or references, listed anywhere on the MediaWiki page
        Note:
            Not settable
        Note
            May include external links within page that are not technically cited anywhere"""
        if self._references is None:
            self._references = []
            self.__pull_combined_properties()
        return self._references

    @property
    def categories(self) -> List[str]:
        """list: Non-hidden categories on the page

        Note:
            Not settable"""
        if self._categories is None:
            self._categories = []
            self.__pull_combined_properties()
        return self._categories

    @property
    def coordinates(self) -> Optional[Tuple[Decimal, Decimal]]:
        """Tuple: GeoCoordinates of the place referenced; results in lat/long tuple or None if no geocoordinates present

        Note:
            Not settable
        Note:
            Requires the GeoData extension to be installed"""
        if self._coordinates is False:
            self._coordinates = None
            self.__pull_combined_properties()
        return self._coordinates  # type: ignore

    @property
    def links(self) -> List[str]:
        """list: List of all MediaWiki page links on the page

        Note:
            Not settable"""
        if self._links is None:
            self._links = []
            self.__pull_combined_properties()
        return self._links

    @property
    def redirects(self) -> List[str]:
        """list: List of all redirects to this page; **i.e.,** the titles listed here will redirect to this page title

        Note:
            Not settable"""
        if self._redirects is None:
            self._redirects = []
            self.__pull_combined_properties()
        return self._redirects

    @property
    def backlinks(self) -> List[str]:
        """list: Pages that link to this page

        Note:
            Not settable"""
        if self._backlinks is None:
            self._backlinks = []
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
    def langlinks(self) -> Dict[str, str]:
        """dict: Names of the page in other languages for which page is where the key is the language code
        and the page name is the name of the page in that language.

        Note:
            Not settable
        Note:
            list of all language links from the provided pages to other
            languages according to: https://www.mediawiki.org/wiki/API:Langlinks"""

        if self._langlinks is None:
            params = {"prop": "langlinks", "cllimit": "max"}
            query_result = self._continued_query(params)

            langlinks = {}
            for lang_info in query_result:
                langlinks[lang_info["lang"]] = lang_info["*"]
            self._langlinks = langlinks
        return self._langlinks

    @property
    def preview(self) -> Dict[str, str]:
        """dict: Page preview information that builds the preview hover"""
        if self._preview is None:
            params = {
                "action": "query",
                "formatversion": "2",
                "prop": "info|extracts|pageimages|revisions|pageterms|coordinates|pageviews",
                "exsentences": "5",
                "explaintext": "true",
                "piprop": "thumbnail|original",
                "pithumbsize": "320",
                "pilicense": "any",
                "rvprop": "timestamp|ids",
                "wbptterms": "description",
                "titles": self.title,
            }
            raw = self.mediawiki.wiki_request(params)
            self._preview = raw.get("query", {}).get("pages", [])[0]
        return self._preview

    @property
    def summary(self) -> Optional[str]:
        """str: Default page summary

        Note:
            Not settable"""
        if self._summary is None:
            self.__pull_combined_properties()
            if self._summary is None:
                self._summary = ""
        return self._summary

    def summarize(self, sentences: int = 0, chars: int = 0) -> str:
        """Summarize page either by number of sentences, chars, or first
        section (**default**)

        Args:
            sentences (int): Number of sentences to use in summary (first `x` sentences)
            chars (int): Number of characters to use in summary (first `x` characters)
        Returns:
            str: The summary of the MediaWiki page
        Note:
            Precedence for parameters: sentences then chars; if both are 0 then the entire first section is returned"""
        query_params: Dict[str, Any] = {"prop": "extracts", "explaintext": "", "titles": self.title}
        if sentences:
            query_params["exsentences"] = min(sentences, 10)
        elif chars:
            query_params["exchars"] = max(chars, 1)
        else:
            query_params["exintro"] = ""

        request = self.mediawiki.wiki_request(query_params)
        return request["query"]["pages"][self.pageid].get("extract")

    @property
    def sections(self) -> List[str]:
        """list: Table of contents sections

        Note:
            Not settable"""
        # NOTE: Due to MediaWiki sites adding superscripts or italics or bold
        #       information in the sections, moving to regex to get the
        #       `non-decorated` name instead of using the query api!
        if self._sections is None:
            self._parse_sections()
            if self._sections is None:
                self._sections = []
        return self._sections

    @property
    def table_of_contents(self) -> Dict[str, Any]:
        """OrderedDict: Dictionary of sections and sub-sections

        Note:
            Leaf nodes are empty OrderedDict objects
        Note:
            Not Settable"""

        if self._table_of_contents is None:
            self._parse_sections()
            if self._table_of_contents is None:
                self._table_of_contents = {}
        return self._table_of_contents

    def section(self, section_title: Optional[str]) -> Optional[str]:
        """Plain text section content

        Args:
            section_title (str): Name of the section to pull or None for the header section
        Returns:
            str: The content of the section
        Note:
            Use **None** if the header section is desired
        Note:
            Returns **None** if section title is not found; only text between title and next \
                section or sub-section title is returned
        Note:
            Side effect is to also pull the content which can be slow
        Note:
            This is a parsing operation and not part of the standard API"""
        if not section_title:
            try:
                content = self.content
                index = 0
            except ValueError:
                return None
            except IndexError:
                pass
        else:
            section = f"== {section_title} =="
            try:
                # TODO, move index to find to remove exceptions
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

        val = self.content[index:next_index].lstrip("=").strip()
        if val == "":
            return None
        return val

    def parse_section_links(self, section_title: str) -> Optional[List[Tuple[str, str]]]:
        """Parse all links within a section

        Args:
            section_title (str): Name of the section to pull or, if  None is provided, \
                the links between the main heading and the first section
        Returns:
            list: List of (title, url) tuples
        Note:
            Use **None** to pull the links from the header section
        Note:
            Returns **None** if section title is not found
        Note:
            Side effect is to also pull the html which can be slow
        Note:
            This is a parsing operation and not part of the standard API"""
        # Cache the results of parsing the html, so that multiple calls happen much faster
        if not self.html:
            return None
        if not self._soup:
            self._soup = BeautifulSoup(self.html, "html.parser")

        if not section_title:
            return self._parse_section_links(None)

        headlines = self._soup.find_all("span", class_="mw-headline")
        tmp_soup = BeautifulSoup(section_title, "html.parser")
        tmp_sec_title = tmp_soup.get_text().lower()
        id_tag = None
        for headline in headlines:
            tmp_id = headline.text
            if tmp_id.lower() == tmp_sec_title:
                id_tag = headline.get("id")
                break

        return self._parse_section_links(id_tag) if id_tag is not None else None

    # Protected Methods
    def __load(self, redirect: bool = True, preload: bool = False):
        """load the basic page information"""
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
        """raise the correct type of page error"""
        if hasattr(self, "title"):
            raise PageError(title=self.title)
        raise PageError(pageid=self.pageid)

    def _raise_disambiguation_error(self, page: Dict, pageid: int):
        """parse and throw a disambiguation error"""
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
        filtered_lis = [li for li in lis if "tocsection" not in "".join(li.get("class", []))]
        may_refer_to = [li.a.get_text() for li in filtered_lis if li.a]

        disambiguation = []
        for lis_item in filtered_lis:
            item = lis_item.find_all("a")
            one_disambiguation = {}
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

    def _handle_redirect(self, redirect: bool, preload: bool, query: Dict, page: Dict[str, Any]):
        """handle redirect"""
        if not redirect:
            raise RedirectError(getattr(self, "title", page["title"]))

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
        self.__init__(  # type: ignore
            self.mediawiki,
            title=redirects["to"],
            redirect=redirect,
            preload=preload,
        )

    def _continued_query(self, query_params: Dict[str, Any], key: str = "pages") -> Iterator[Dict[Any, Any]]:
        """Based on
        https://www.mediawiki.org/wiki/API:Query#Continuing_queries"""
        query_params.update(self.__title_query_param())

        last_cont: Dict = {}
        prop = query_params.get("prop")

        while True:
            params = query_params.copy()
            params.update(last_cont)

            request = self.mediawiki.wiki_request(params)

            if "query" not in request:
                break

            pages = request["query"][key]
            if "generator" in query_params:
                yield from pages.values()
            elif isinstance(pages, list):
                yield from [v for x, v in enumerate(pages)]
            else:
                yield from pages[self.pageid].get(prop, [])

            if "continue" not in request or request["continue"] == last_cont:
                break

            last_cont = request["continue"]

    def _parse_section_links(self, id_tag: Optional[str]) -> List[Tuple[str, str]]:
        """given a section id, parse the links in the unordered list"""
        all_links: List[Tuple[str, str]] = []

        if not self._soup:
            self._soup = BeautifulSoup(self.html, "html.parser")

        if id_tag is None:
            root = self._soup.find("div", {"class": "mw-parser-output"})
            if root is None or isinstance(root, NavigableString):
                return all_links
            candidates = root.children
        else:
            root = self._soup.find("span", {"id": id_tag})
            if root is None:
                return all_links
            candidates = self._soup.find(id=id_tag).parent.next_siblings  # type: ignore

        for node in candidates:
            if not isinstance(node, Tag) or node.get("role", "") == "navigation":
                continue
            classes = node.get("class", [])
            if not isinstance(classes, list):
                classes = [classes if classes else ""]
            if "infobox" in classes:
                continue

            # If the classname contains "toc", the element is a table of contents.
            # The comprehension is necessary because there are several possible
            # types of tocs: "toclevel", "toc", ...
            toc_classnames = [cname for cname in classes if "toc" in cname]
            if toc_classnames:
                continue

            # this is actually the child node's class...
            is_headline = node.find("span", {"class": "mw-headline"})
            if is_headline is not None:
                break
            if node.name == "a":
                all_links.append(self.__parse_link_info(node))
            else:
                all_links.extend(self.__parse_link_info(link) for link in node.find_all("a"))
        return all_links

    def __parse_link_info(self, link: Tag) -> Tuple[str, str]:
        """parse the <a> tag for the link"""
        href = link.get("href", "")
        if isinstance(href, list):
            href = href[0]
        href = "" if href is None else href
        txt = link.string or href
        is_rel = is_relative_url(href)
        if is_rel is True:
            tmp = f"{self.mediawiki.base_url}{href}"
        elif is_rel is None:
            tmp = f"{self.url}{href}"
        else:
            tmp = href
        return txt, tmp

    def _parse_sections(self):
        """parse sections and TOC"""

        def _list_to_dict(_dict, path, sec):
            tmp = _dict
            for elm in path[:-1]:
                tmp = tmp[elm]
            tmp[sec] = OrderedDict()

        self._sections = []
        section_regexp = r"\n==* .* ==*\n"  # '== {STUFF_NOT_\n} =='
        found_obj = re.findall(section_regexp, self.content)

        res = OrderedDict()
        path = []
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
                while last_depth > depth:
                    path.pop()
                    last_depth -= 1
                if path:
                    path.pop()
                path.append(sec)
                _list_to_dict(res, path, sec)
                last_depth = depth
            else:
                if path:
                    path.pop()
                path.append(sec)
                _list_to_dict(res, path, sec)
                last_depth = depth
            self._sections.append(sec)

        self._table_of_contents = res

    def __title_query_param(self) -> Dict[str, Any]:
        """util function to determine which parameter method to use"""
        if getattr(self, "title", None) is not None:
            return {"titles": self.title}
        return {"pageids": self.pageid}

    def __pull_combined_properties(self):
        """something here..."""

        query_params = {
            "titles": self.title,
            "prop": "extracts|redirects|links|coordinates|categories|extlinks",
            "continue": {},
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

        last_cont = {}
        results = {}
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
        tmp = [link["title"] for link in results.get("redirects", [])]
        self._redirects = sorted(tmp)

        # summary
        self._summary = results.get("extract")

        # links
        tmp = [link["title"] for link in results.get("links", [])]
        self._links = sorted(tmp)

        # categories
        def _get_cat(val):
            """parse the category correctly"""
            tmp = val["title"]
            if tmp.startswith(self.mediawiki.category_prefix):
                return tmp[len(self.mediawiki.category_prefix) + 1 :]
            return tmp

        tmp = [_get_cat(link) for link in results.get("categories", [])]
        self._categories = sorted(tmp)

        # coordinates
        if "coordinates" in results:
            self._coordinates = (
                Decimal(results["coordinates"][0]["lat"]),
                Decimal(results["coordinates"][0]["lon"]),
            )

        # references
        tmp = [link["*"] for link in results.get("extlinks", [])]
        self._references = sorted(tmp)
