
## Welcome!!

Welcome to the pymediawiki: a python MediaWiki API wrapper project. I hope that
you have found the project to be useful. If you are here, you must want to help
out in some way! I am very grateful for any help and support.

### Table Of Contents
* [Contributing](#contributing)
* [Issues and Bug Reports](#issues-and-bug-reports)
* [Enhancement Requests](#enhancements)
* [Submitting Pull Requests](#pull-requests)
* [Testing](#testing)
* [Coding Style](#coding-style)
* [Code Contributors](#code-contributors)

### Contributing

Contributing to open-source software comes in many forms: adding additional
functionality, reporting and/or fixing bugs and defects, and helping maintain
documentation. Any and all forms are welcome!

Below you will find ways to help the project along with notes on how to report
bugs and issues, request enhancements, and issue pull requests.

#### Issues and Bug Reports

If you have found an issue with `pymediawiki`, please do not hesitate to let us
know! Before submitting an issue or bug report, we ask that you complete a few
cursory items:

* **Review** current bugs to see if your issue has already been reported. If it
has been previously reported, please comment on the original report with any
additional details. This will help the maintainers triage the issue more
quickly.

* **Ensure** that the issue is **not** related to the MediaWiki site you are
trying to which you are trying to connect. There are times where the MediaWiki
site may refuse connections or throw an error. There are times when trying
again is all that is needed! If the error is the MediaWiki site, please do not
report an issue as there is nothing we can do to help. If, however it is
something within the library, please do not hesitate to report the issue!

* **Determine** that the issue is reproducible - a code sample of the issue
will help narrow down the search for the cause of the issue and may lead to a
quicker fix!

A **great bug report** will consist of the following:

* A descriptive title

* A brief description of the issue

* Description of the expected results

* A code example to reproduce the error. Please use
[Markdown code blocks](https://help.github.com/articles/creating-and-highlighting-code-blocks/)
with syntax highlighting

* The link to the API URL if not the default:
[Wikipedia API](http://en.wikipedia.org/w/api.php)

* The affected version(s) of `pymediawiki`

#### Enhancements

Enhancements are additional functionality not currently supported by the
`pymediawiki` library. Unfortunately, not all enhancements make sense for the
goal of the project. If you have a desired feature, there are a few things you
can do to possibly help get the feature into the `pymediawiki` library:

* **Review** to see if the feature has been requested in the past.

    * If it is requested and still open, add your comment as to why you would
    like it.

    * If it was previously requested but closed, you may be interested in why
    it was closed and not implemented. I will try to explain my reasoning for
    not supporting actions as much as possible.

* Add an issue to the
[issue tracker](https://github.com/barrust/mediawiki/issues) and mark it as an
enhancement. A ***great enhancement*** request will have the following
information:

    * A descriptive title

    * A description of the desired functionality: use cases, added benefit to
    the library, etc.

    * A code example, if necessary, to explain how the code would be used

    * A description of the desired results

#### Pull Requests

Pull requests are how you will be able to add new features, fix bugs, or update
documentation in the pymediawiki library. To create a pull request, you will
first need to fork the repository, make all necessary changes and then create
a pull request. There are a few guidelines for creating pull requests:

* All pull requests must be based off of the latest development branch and not
master (unless there is not a development branch!)

* If the PR only changes documentation, please add `[ci skip]` to the commit
message. To learn more, you can [read about skipping integration testing](https://docs.travis-ci.com/user/customizing-the-build#Skipping-a-build)

* Reference ***any and all*** [issues](https://github.com/barrust/mediawiki/issues)
related to the pull request

#### Testing

Each pull request should add or modify the appropriate tests. pymediawiki uses
the unittest module to support tests and most are currently found in the
`./tests/mediawiki_test.py` file.

The `./scripts/generate_test_data.py` file is used to help capture request and
response data in different json files for running tests without internet
access.

* ###### New Feature:
    * Add tests for each variation of the new feature

* ###### Bug Fix
    * Add at least one regression test of an instance that is working to help
    ensure that the bug fix does not cause a new bug

    * Add at least one test to show the corrected outcome from the updated code
    to help ensure that the code works as intended

#### Coding Style

The MediaWiki API wrapper project follows the
[PEP8](https://www.python.org/dev/peps/pep-0008/) coding style for consistency
and readability. Code that does not comply with PEP8 will not be accepted into
the project as-is. All code should adhere to the PEP8 coding style standard
where possible.

The MediaWiki API wrapper project also uses [pylint](https://www.pylint.org/)
to help identify potential errors, code duplication, and non-pythonic syntax.
Adhering to pylint's results is not strictly required.

To install the [PEP8 compliance checker](https://pypi.org/project/pycodestyle/),
you can simply run the following:

```
pip install pycodestyle
```

To test for PEP8 compliance, run the following from the root directory:

```
pep8 mediawiki
```

### Code Contributors:

A special thanks to all the code contributors to `pymediawiki`!

[@barrust](https://github.com/barrust) (Maintainer)

[@dan-blanchard](https://github.com/dan-blanchard) - Default URL conforms to passed in language [#26](https://github.com/barrust/mediawiki/pull/26)

[@nagash91](https://github.com/nagash91) - Pull section titles without additional markup [#42](https://github.com/barrust/mediawiki/issues/42)

[@flamableconcrete](https://github.com/flamableconcrete) - Added `allpages` functionality [#75](https://github.com/barrust/mediawiki/pull/75)

[@shnela](https://github.com/shnela) - Added `langlinks` property [#65](https://github.com/barrust/mediawiki/issues/65)

[rubabredwan](https://github.com/rubabredwan) - Fix for `suggest` [#85](https://github.com/barrust/mediawiki/pull/85)
