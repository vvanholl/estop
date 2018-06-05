#!/usr/bin/env python

from setuptools import setup, find_packages

with open('VERSION') as version_file:
    version = version_file.read()

with open('README.rst') as readme_file:
    long_description = readme_file.read()

with open('requirements.txt') as requirements_file:
    install_requires = requirements_file.read().splitlines()

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.0',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: System :: Clustering',
    'Topic :: System :: Networking',
    'Topic :: System :: Networking :: Monitoring',
    'Topic :: Utilities',
]

scripts = [
    'bin/estop'
]

setup(
    name='estop',
    version=version,
    description='Monitor and control Elasticsearch tasks',
    long_description=long_description,
    url='https://github.com/vvanholl/estop',
    author='Vincent Van Hollebeke',
    author_email='vincent@compuscene.org',
    license='Apache License, Version 2.0',
    install_requires=install_requires,
    classifiers=classifiers,
    packages=find_packages(exclude=('tests',)),
    scripts=scripts
)
