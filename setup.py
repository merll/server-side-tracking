# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from server_tracking import __version__

setup(
    name='server-side-tracking',
    version=__version__,
    packages=find_packages(),
    url='',
    license='MIT',
    author='Matthias Erll',
    author_email='matthias@erll.de',
    install_requires=['requests', 'six'],
    description='Server-side tracking in Google Analytics for web applications.'
)
