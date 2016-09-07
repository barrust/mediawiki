
import setuptools

import sys
sys.dont_write_bytecode = True

from mediawiki import (__version__, __author__, __license__, __email__, MediaWiki)

setuptools.setup(
    name = "mediawiki",
    version = __version__,
    author = __author__,
    author_email = __email__,
    description = "MediaWiki API for Python",
    license = __license__,
    keywords = "python mediawiki wikipedia API",
    url = "https://github.com/barrust/mediawiki",
    install_requires = ['beautifulsoup4', 'requests>=2.0.0,<3.0.0'],
    packages = ['mediawiki'],
    long_description = 'NEED TO WRITE A LONG DESCRIPTION',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
    test_suite="tests"
)
