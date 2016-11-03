#!/usr/bin/env python
from setuptools import setup, find_packages
import sys


long_description = ''

if 'upload' in sys.argv:
    with open('README.rst') as f:
        long_description = f.read()


setup(
    name='kwo',
    version='0.1.0',
    description='Python 2/3 compatible keyword only arguments.',
    author='Joe Jevnik',
    author_email='joejev@gmail.com',
    packages=find_packages(),
    long_description=long_description,
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Pre-processors',
    ],
    url='https://github.com/llllllllll/kwo',
    extras_require={
        'dev': [
            'flake8==2.4.0',
            'pytest==2.8.4',
            'pytest-cov==2.2.1',
            'pytest-pep8==1.0.6',
        ],
    },
)
