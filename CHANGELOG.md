# MediaWiki Changelog

## Current

### Version 0.3.11

* Re-factored MediaWikiPage into its own file
* Better Unicode support

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
