# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='twitter-classifier',
    version='0.1.0',
    description='Twitter classifier',
    long_description=readme,
    author='Matthew Killi',
    author_email='matthew.p.killi@gmail.com',
    url='https://github.com/mkilli83/Twitter.git',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

