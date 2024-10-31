# MediaWiki Changelog

## Version 0.7.5

* Move configuration items to a configuration data class
  * Will allow for the deprication of some top level properties in lieu of changing against the `Configuration` class
* Added HTTPAuthenticator for web server authentication; [PR #141](https://github.com/barrust/mediawiki/pull/141) Thanks [gbenson](https://github.com/gbenson)

## Version 0.7.4

* Add typing support

## Version 0.7.3

* Add `unordered_options` to the `DisambiguationError` to attempt to get options in the order presented on the page; [issue #124](https://github.com/barrust/mediawiki/issues/124)
* Add [verify SSL support](https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification) by passing info directly to the requests library.

## Version 0.7.2

* Add `page_preview` property to simulate the page preview hover [PR #114](https://github.com/barrust/mediawiki/pull/114)
* Add `available_languages` property [PR #116](https://github.com/barrust/mediawiki/pull/116)

## Version 0.7.1

* Add `page.wikitext` support for pulling the page contents as [wikitext](https://en.wikipedia.org/wiki/Help:Wikitext)
* Add [proxy support](https://requests.readthedocs.io/en/master/user/advanced/#proxies) by passing info directly to the requests library.

## Version 0.7.0

* Remove support for ***python 2.7***!
* Add files to `categorymembers()` pull [PR #100](https://github.com/barrust/mediawiki/pull/100) Thanks [tbm](https://github.com/tbm)
* Better support calls to limit results to the maximum 500 results per query (per API documentation) [PR #99](https://github.com/barrust/mediawiki/pull/99) Thanks [tbm](https://github.com/tbm)

## Version 0.6.7

* ***NOTE:*** Last planned support for **Python 2.7**
* Cache results of `BeautifulSoup` parsing of `page.html` [PR #90](https://github.com/barrust/mediawiki/pull/90) Thanks [ldorigo](https://github.com/ldorigo)
* Add ability to pull links from the header section; Thanks to [ldorigo](https://github.com/ldorigo) for example code!
* Add ability to pull the header section text
* Move to GitHub Actions and CodeCov for testing

## Version 0.6.6

* Fix a bug using `find_all()` on newer versions of BeautifulSoup4

## Version 0.6.5

* Fix for `suggest` [PR #85](https://github.com/barrust/mediawiki/pull/85) Thanks [rubabredwan](https://github.com/rubabredwan)
* `__slots__` usage

## Version 0.6.4

* Add ability to login during initialization [issue #79](https://github.com/barrust/mediawiki/issues/79)

## Version 0.6.3

* Capture timeout exception
* bs4 does not support `hasattr` but uses `*.has_attr()`

## Version 0.6.2

* Add `allpages` functionality [PR #75](https://github.com/barrust/mediawiki/pull/75)
* Add `langlinks` page property [PR #76](https://github.com/barrust/mediawiki/pull/76)

## Version 0.6.1

* Fix DisambiguationError title property [issue #72](https://github.com/barrust/mediawiki/issues/72)
* Change to using [black](https://github.com/ambv/black) formatting

## Version 0.6.0

* Fix for the table of contents for all subsections [issue #64](https://github.com/barrust/mediawiki/issues/64)
* Combined properties into a single set of pulling to reduce the load on the MediaWiki infrastructure [issue #55](https://github.com/barrust/mediawiki/issues/55)

## Version 0.5.1

* Added Table of Contents parsing based on sections: result is an OrderedDict
* Fix issue where some sections are not pulled correctly

## Version 0.5.0

* Add support for logging into the MediaWiki site [issue #59](https://github.com/barrust/mediawiki/issues/59)

## Version 0.4.1

* Default to `https`
* Add `category_prefix` property to properly support categories in non-English
MediaWiki sites [issue #48](https://github.com/barrust/mediawiki/issues/48)
* Add `user_agent` as an initialization parameter and added information to the
documentation about why one should set the user-agent string [issue #50](https://github.com/barrust/mediawiki/issues/50)

### Version 0.4.0

* Add fix to use the `query-continue` parameter to continue to pull category
members [issue #39](https://github.com/barrust/mediawiki/issues/39)
* Better handle large categorymember selections
* Add better handling of exception attributes including adding them to the
documentation
* Correct the pulling of the section titles without additional markup [issue #42](https://github.com/barrust/mediawiki/issues/42)
* Handle memoization of unicode parameters in python 2.7
* ***Change default timeout*** for HTTP requests to 15 seconds

### Version 0.3.16

* Add ability to turn off caching completely
* Fix bug when disambiguation link does not have a title [issue #35](https://github.com/barrust/mediawiki/issues/35)

### Version 0.3.15

* Add parse all links within a section [issue #33](https://github.com/barrust/mediawiki/issues/33)
* Add base url property to mediawiki site

### Version 0.3.14

* Add refresh interval to cached responses (Defaults to not refresh)
[issue #30](https://github.com/barrust/mediawiki/issues/30)
* Fix minor documentation issues

### Version 0.3.13

* Add pulling hatnotes [issue #6](https://github.com/barrust/mediawiki/issues/6)
* Add pulling list of main images or logos [issue #28](https://github.com/barrust/mediawiki/issues/28)

### Version 0.3.12

* Default API URL is now language specific: [PR #26](https://github.com/barrust/mediawiki/pull/26)

### Version 0.3.11

* Re-factor MediaWikiPage into its own file
* Remove setting properties outside of **init**()
* Better Unicode support
* Add CONTRIBUTING.md file

### Version 0.3.10

* Add categorytree support
* Remove adding 'http:' to references if missing

### Version 0.3.9

* Fix infinite loop on continued queries: [issue #15](https://github.com/barrust/mediawiki/issues/15)
* Check by looking at the continue variable over time; if it is the same, exit
* Fix image with no url: [issue #14](https://github.com/barrust/mediawiki/issues/14)

### Version 0.3.8

* Fix empty disambiguation list items

### Version 0.3.7

* Memoize support default parameters
* Add support test for Python 3.6

### Version 0.3.6

* Updated Exception documentation
* Fix badges in Readme file
* Additional test coverage

### Version 0.3.5

* Add documentation to README
  * Quickstart information
  * pip install instructions [pypi - pymediawiki](https://pypi.python.org/pypi/pymediawiki/)
  * Additional testing

### Version 0.3.4

* Update documentation
* Better continuous integration
* Better test data: [issue #4](https://github.com/barrust/mediawiki/issues/4)
* First version on PyPi: [issue #8](https://github.com/barrust/mediawiki/issues/8)

### Version 0.3.3

* Improve testing strategy
* Move tests to json from pickle
* Improve parameter checking for geosearch
* Code standardization
* Pep8
* Pylint
* Single quote strings

### Version 0.3.2

* OpenSearch functionality
* PrefixSearch functionality

### Version 0.3.1

* Page Summary
* Page Sections
* Enforce sorting of page properties

### Pre-Version 0.3.1

* Add MediaWiki class
* Add MediaWikiPage class
* Stubbed out functionality
* Add page properties
