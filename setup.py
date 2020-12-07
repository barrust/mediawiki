""" Module Installation script """
import setuptools
import io
from mediawiki import (
    __version__,
    __author__,
    __license__,
    __email__,
    __url__,
    __bugtrack_url__,
)


def read_file(filepath):
    """ read the file """
    with io.open(filepath, "r") as filepointer:
        res = filepointer.read()
    return res


KEYWORDS = [
    "python",
    "mediawiki",
    "wikipedia",
    "API",
    "wiki",
    "parser",
    "natural language processing",
    "nlp",
]

setuptools.setup(
    name="pymediawiki",  # mediawiki was taken
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="Wikipedia and MediaWiki API wrapper for Python",
    license=__license__,
    keywords=" ".join(KEYWORDS),
    url=__url__,
    download_url="{0}/tarball/v{1}".format(__url__, __version__),
    bugtrack_url=__bugtrack_url__,
    install_requires=read_file("requirements.txt").splitlines(),
    packages=["mediawiki"],
    long_description=read_file("README.rst"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Wiki",
        "License :: OSI Approved",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    test_suite="tests",
)
