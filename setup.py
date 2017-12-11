#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script."""
from setuptools import find_packages, setup
import toml

from tegenaria import __version__

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

pip_file = toml.load(open('Pipfile'))
# TODO: Get pinned versions or commits from Git. This solution looks better: https://stackoverflow.com/a/47594760
requirements = list(pip_file['packages'].keys())
test_requirements = list(pip_file['dev-packages'].keys())


setup(
    name='tegenaria',
    version=__version__,
    description='Scrapy spiders to collect different items.',
    long_description=readme + '\n\n' + history,
    author='Wagner Augusto Andreoli',
    author_email='andreoliwa@gmail.com',
    url='https://github.com/andreoliwa/scrapy-tegenaria',
    packages=find_packages(exclude=('tests',)),
    package_dir={'tegenaria': 'tegenaria'},
    include_package_data=True,
    install_requires=requirements,
    license='BSD',
    zip_safe=False,
    keywords='tegenaria',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [],
    }
)
