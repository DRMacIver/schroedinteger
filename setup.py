# coding=utf-8

# This file is part of schroedinteger
# https://github.com/DRMacIver/schroedinteger)

# Most of this work is copyright (C) 2013-2015 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others, who hold
# copyright over their individual contributions.

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# END HEADER

import os

from setuptools import find_packages, setup


def local_file(name):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))

SOURCE = local_file("src")
README = local_file("README.rst")


# Assignment to placate pyflakes. The actual version is from the exec that
# follows.
__version__ = None

with open(local_file("src/schroedinteger/version.py")) as o:
    exec(o.read())

assert __version__ is not None

setup(
    name='schroedinteger',
    version=__version__,
    author='David R. MacIver',
    author_email='david@drmaciver.com',
    packages=find_packages(SOURCE),
    package_dir={"": SOURCE},
    url='https://github.com/DRMacIver/schroedinteger',
    license='MPL v2',
    description='A terrible testing hack',
    zip_safe=False,
    long_description=open(README).read(),
)
