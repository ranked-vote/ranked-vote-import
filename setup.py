#!/usr/bin/env python

from setuptools import setup

setup(name='ranked-vote-import',
      version='0.0.1',
      description='Tools for importing ranked-vote data',
      author='Paul Butler',
      author_email='rcv@paulbutler.org',
      url='https://github.com/ranked-vote/ranked-vote-importers',
      packages=['ranked_vote_import'],
      entry_points={
          'console_scripts': [
              'rcv-import = ranked_vote_import.bin.import_rcv_data:main'
          ]
      },
      install_requires=[
          'pandas>=0.23.4',
          'ranked-vote>=0.0.1'
      ],
      python_requires='>=3.6',
      )
