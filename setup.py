#!/usr/bin/env python
from setuptools import setup, find_packages
import sys

py2 = sys.version_info<(3,)

with open('requirements.txt') as f:
    INSTALL_REQUIRES = [x.strip() for x in f.readlines()]

with open('requirements-dev.txt') as f:
    TEST_REQUIRES = [x.strip() for x in f.readlines()]

with open('README.md') as f:
    readme = f.read()

setup(
    name = "plantmeter",
    version = "1.7.8",
    description =
        "OpenERP module and library to manage multisite energy generation",
    author = "Som Energia SCCL",
    author_email = "info@somenergia.coop",
    url = 'https://github.com/Som-Energia/plantmeter',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    license = 'GNU General Public License v3 or later (GPLv3+)',
    packages=find_packages(exclude=['*[tT]est*']),
    include_package_data = True,
    install_requires=INSTALL_REQUIRES,
    setup_requires=["pytest-runner"],
    tests_require=TEST_REQUIRES,
    test_suite = 'plantmeter',
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],
)

