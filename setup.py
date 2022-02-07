#!/usr/bin/env python
from setuptools import setup, find_packages
import sys
readme = open("README.md").read()

py2 = sys.version_info<(3,)

setup(
	name = "plantmeter",
	version = "1.7.3",
	description =
		"OpenERP module and library to manage multisite energy generation",
	author = "Som Energia SCCL",
	author_email = "info@somenergia.coop",
	url = 'https://github.com/Som-Energia/plantmeter',
	long_description = readme,
    long_description_content_type = 'text/markdown',
	license = 'GNU General Public License v3 or later (GPLv3+)',
	packages=find_packages(exclude=['*[tT]est*']),
	install_requires=[
        'somutils',
        'pymongo<4',
        'numpy<1.17' if py2 else 'numpy', # Py2
        'xlrd',
        'yamlns',
        'pytz',
        'erppeek',
        'consolemsg',
        'mock',
        'b2btest',
        'pytest',
        'pytest-cov<3' if py2 else 'pytest-cov', # Py2
	],
	include_package_data = True,
	test_suite = 'plantmeter',
#	test_runner = 'colour_runner.runner.ColourTextTestRunner',
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

