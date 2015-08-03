# gtr-tools

A set of Python scripts to work with data in the [NIH Genetic Testing Registry (GTR)](http://www.ncbi.nlm.nih.gov/gtr/).

## Installation

These programs all run in Python 2.7.

1. Install [Python 2.7](https://www.python.org/downloads/) to your computer.* 
    - You will also need [pip](https://github.com/pypa/pip), this is included starting in Python 2.7.9, so if you
have an older version and do not have pip, install pip. 
2. Then clone/download this repository
3. cd to its location
4. then in the terminal enter:
`pip install -r requirements.txt`

*note:  for scientific computing, I suggest installing [Continuum's Anaconda](https://store.continuum.io/cshop/anaconda/). It already includes all the modules
needed to run these scripts, and many others which makes installation of frequently used non-built-in modules easier, it does not
affect other python installations on your machine, and the conda package manager is a great way to handle
virtual environments. This is useful if you are interested in also installing the most current stable release of Python 3 on the same system.

## search

Search provides a GUI program for searching GTR and downloading data. It utilizes the E-utilities.

## ngs

NGS is a hot topic in bioinformatics and genetic testing. These scripts provide some insight into 
the growth of NGS in the GTR and best practices for that data.