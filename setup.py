# -*- coding: utf-8 -*-
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='quantlplot',
    version='1.7',
    author='Shamaz Khan',
    author_email='shamaz.khan@outlook.com',
    description='Finance plotting for Quantl',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/shamazkhan/quantlplot',
    packages=['quantlplot'],
    install_requires=['pandas', 'PyQt5', 'pyqtgraph>=0.11.1'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
