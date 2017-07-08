'''
Module Installation script
'''
import setuptools

from mediawiki import (__version__, __author__, __license__, __email__,
                       __url__)

setuptools.setup(
    name = 'pymediawiki',  # mediawiki was taken
    version = __version__,
    author = __author__,
    author_email = __email__,
    description = 'Wikipedia and MediaWiki API wrapper for Python',
    license = __license__,
    keywords = 'python mediawiki wikipedia API wiki parse',
    url = __url__,
    download_url = '{0}/tarball/v{1}'.format(__url__, __version__),
    install_requires = ['beautifulsoup4', 'requests>=2.0.0,<3.0.0'],
    packages = ['mediawiki'],
    long_description = open('README.rst', 'r').read(),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Wiki',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    test_suite = 'tests'
)
