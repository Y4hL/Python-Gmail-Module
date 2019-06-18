import io
from setuptools import setup
import os


# Package meta-data.
NAME = 'Python-Gmail-Module'
PACKAGES = ['PGM']
DESCRIPTION = 'Easily Send and Receive Mails with Python\nConveniently Send and Download Attachements'
URL = 'http://github.com/Y4hL/Python-Gmail-Module'
EMAIL = 'rasmus.kinnunen1@gmail.com'
AUTHOR = 'Y4hL'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.2.0'



here = os.path.dirname(os.path.abspath(__file__))

# Required Packages
try:
    with io.open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as e:
        REQUIRED = e.read().splitlines()
except FileNotFoundError:
    REQUIRED = []

# Optional Packages
EXTRAS = {

    # 'Feature Name': ['Extra Package']
    
    }

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in the MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# Setup
setup(
    name=NAME,
    packages=PACKAGES,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type='text/markdown',
    install_requires=REQUIRED,
    licence="GNU GPLv3",
    version=VERSION,
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    tests_require=[],
    include_package_data=True,
    python_requires=REQUIRES_PYTHON,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Email Clients (MUA)',
    ],
)
