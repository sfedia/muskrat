#!/usr/bin/python3

import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="muskrat",
    version="0.0.1",
    author="Fyodor Sizov",
    author_email="f.sizov@yandex.ru",
    description="Minimalistic non-BNF text parser",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/prodotiscus/muskrat",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later",
        "Operating System :: OS Independent",
    ),
)