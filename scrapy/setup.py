#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tegenaria

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

with open('requirements/prod.txt') as txt_file:
    lines = txt_file.read()
requirements = [line for line in lines.split('\n') if '=' in line]

with open('requirements/dev.txt') as txt_file:
    lines = txt_file.read()
test_requirements = [line for line in lines.split('\n') if '=' in line]
test_requirements.extend(requirements)


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(
    name='tegenaria',
    version=tegenaria.__version__,
    description="Scrapy spiders to collect different items.",
    long_description=readme + '\n\n' + history,
    author="Wagner Augusto Andreoli",
    author_email='wagnerandreoli@gmail.com',
    url='https://github.com/andreoliw/python-tegenaria',
    packages=[
        'tegenaria',
    ],
    package_dir={'tegenaria':
                 'tegenaria'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='tegenaria',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
    ],
    cmdclass={'test': PyTest},
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [],
    }
)
