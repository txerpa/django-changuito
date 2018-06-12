# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

from setuptools import setup

setup(
    name='django-changuito',
    version='1.2',
    description='A fork of a fork django-cart '
                'with the same simplicity but updated',
    maintainer='Alberto Pou',
    maintainer_email='alberto.pou@txerpa.com',
    license='LGPL v3',
    url='https://github.com/txerpa/django-changuito',
    packages=['changuito'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
