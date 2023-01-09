#!/usr/bin/env python3

from distutils.core import setup
setup(
    name='magicmain',
    version='0.2',
    python_requires='>=2.7',
    options={'bdist_wheel':{'universal':'1'}},
    description='Make appendable dependency zips',
    author='Oren Tirosh',
    author_email='orent@hishome.net',
    url='http://github.com/orent/magicmain',
    py_modules=['__main__'],
)
