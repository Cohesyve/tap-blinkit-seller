#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap_blinkit_seller',
      version='0.0.2',
      description='Singer.io tap for extracting data from the Blinkit Advertising API',
      author='Cohesyve',
      url='http://cohesyve.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_blinkit_seller'],
      install_requires=[
          'tap-framework @ git+https://github.com/hotgluexyz/tap-framework.git#egg=tap-framework', # USING THE HOTGLUE VERSION
      ],
      entry_points='''
          [console_scripts]
          tap_blinkit_seller=tap_blinkit_seller:main
      ''',
      packages=find_packages(),
      package_data={
          'tap_blinkit_seller': [
              'schemas/*.json'
          ]
      })
