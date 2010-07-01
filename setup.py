#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "wacfg",
    version = __import__('wacfg').__version__(),
    description = 'Webapp-config reloaded',
    author = 'Andreas Nüßlein',
    author_email = 'nutz@noova.de',
    url = 'http://notyetset.com',
    license = "BSD",
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
)
