#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name = "wacfg",
    version = __import__('wacfg').__version__(),
    description = 'Webapp-config reloaded',
    author = 'Andreas Nuesslein',
    author_email = 'nutz@noova.de',
    url = 'http://git.noova.de/wacfg',
    license = "CDDL",
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
)
