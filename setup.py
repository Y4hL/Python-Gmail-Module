import os
import io
from setuptools import setup


# Package meta-data.
NAME = 'mailpy'
PACKAGES = ['mailpy']
DESCRIPTION = 'Easily Send and Receive Mails with Python'
URL = 'http://github.com/Y4hL/mailpy'
EMAIL = 'rasmus.kinnunen1@gmail.com'
AUTHOR = 'https://github.com/Y4hL'
REQUIRES_PYTHON = '>=3.5.0'
VERSION = '0.0.5'


here = os.path.dirname(os.path.abspath(__file__))

def read(filename):
    """ This function is reads in the file with the file path """
    filepath = os.path.join(here, filename)
    with io.open(filepath, mode="r", encoding="utf-8") as f:
        return f.read()

# Required Packages
REQUIRED = read('requirements.txt').splitlines()

# Optional Packages
EXTRAS = {

    # 'Feature Name': ['Extra Package']
    
    }



# Setup
setup(
    name=NAME,
    packages=PACKAGES,
    description=DESCRIPTION,
    long_description=read('README.md'),
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
    # setup_requires=[],
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
