from setuptools import setup
from os import path

DIR = path.dirname(path.abspath(__file__))
INSTALL_PACKAGES = open(path.join(DIR, 'requirements.txt')).read().splitlines()

with open(path.join(DIR, 'README.md')) as f:
    README = f.read()

setup(
    name='Python-Gmail-Module',
    packages=['PGM'],
    description="Easily Send, Read and Download attachments from Gmail with Python",
    long_description=README,
    long_description_content_type='text/markdown',
    install_requires=INSTALL_PACKAGES,
    version='v0.1',
    url='http://github.com/Y4hL/Python-Gmail-Module',
    author='Y4hL',
    author_email='rasmus.kinnunen1@gmail.com',
    keywords=['gmail', 'smtp', 'email', 'python'],
    tests_require=[],
    package_data={
        # include json and pkl files
        '': ['PGM\\*.json'],
    },
    include_package_data=True,
    python_requires='>=3'
)
