#!/usr/bin/env python
# -*- coding: utf-8 -*-
import home_spider

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
    name='home_spider',
    version=home_spider.__version__,
    description="Search for a home.",
    long_description=readme + '\n\n' + history,
    author="Wagner Augusto Andreoli",
    author_email='wagnerandreoli@gmail.com',
    url='https://github.com/wagnerandreoli/python-home-spider',
    packages=[
        'home_spider',
    ],
    package_dir={'home_spider':
                 'home_spider'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='home_spider',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    cmdclass={'test': PyTest},
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            # TODO: Put command line scripts here
            # 'my-cli-script = home_spider.my_module:MyClass.main',
            # 'my-other-cli-script = home_spider.another_module:some_function'
        ],
    }
)
