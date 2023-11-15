"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
# To use a consistent encoding
from codecs import open
from os import listdir, path, walk

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

from pathlib import Path

PROJECT_PATH = Path(__file__).parent

# Get requirements for current package
with (PROJECT_PATH / "requirements.txt").open() as f:
    install_requires = [l.strip() for l in f.readlines()]


# Get the long description from the README file
def _get_long_description():
    description = PROJECT_PATH.joinpath("README.md").read_text(encoding="utf-8")

    return description


# Get version
def _get_version():
    with PROJECT_PATH.joinpath("github_publish", "version.py").open() as f:
        line = next(line for line in f if line.startswith("__version__"))

    version = line.partition("=")[2].strip()[1:-1]

    return version


setup(
    name="github_publish",
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=_get_version(),
    description="GitHub publisher",
    long_description=_get_long_description(),
    # The project's main homepage.
    url="http://github.com/umihai1/github_publish",
    # Author details
    author="umihai1",
    author_email="umihai1@yahoo.com",
    # Choose your license
    license="MIT License",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        # Indicate who your project is intended for
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        # Pick your license as you wish (should match "license" above)
        "License :: Public Domain",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    # What does your project relate to?
    keywords="handles releases on a GitHub.com server",
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=["contrib", "doc", "test"]),
    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=install_requires,
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={},
    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={},
    # include_package_data=True,
    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #    entry_points={
    #        'console_scripts': [
    #            'sample=sample:main',
    #        ],
    #    },
)
