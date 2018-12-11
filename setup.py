#!/usr/bin/python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="muskrat",
    version="1.0.12",
    author="Fyodor Sizov",
    author_email="f.sizov@yandex.ru",
    description="Minimalistic non-BNF text parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prodotiscus/muskrat",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)
