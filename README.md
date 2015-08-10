# gtr-tools

A set of Python scripts to work with data in the [NIH Genetic Testing Registry (GTR)](http://www.ncbi.nlm.nih.gov/gtr/).

### Installation

These programs all run in Python 2.7.

Recommended:

To skip all the steps below, I suggest installing [Continuum's Anaconda](https://store.continuum.io/cshop/anaconda/), 
which I highly recommend for scientific computing. It already includes all the modules
needed to run these scripts, and many others which makes installation of frequently used non-built-in modules easier, it does not
affect other python installations on your machine, and the conda package manager is a great way to handle
virtual environments.

Traditional, cumbersome way:

1. If you do not already have Python 2.7, Install [Python 2.7](https://www.python.org/downloads/) to your computer.
    * If you already have Python 2.7, you will also need [pip](https://github.com/pypa/pip). This is included starting in Python 2.7.9, so if you
have an older version and do not have pip, install pip. 
2. Then clone/download this repository
3. cd to its location
4. *then in the terminal enter:
`pip install -r requirements.txt`

*Note: The above steps may require even extra effort to get installed onto osx/linux. lxml may require more dependencies to
be installed which can be difficult. Also, tkinter is not in the requirements.txt since it is a built-in but certain
versions of OSX/Linux and their shipped Python version do not include it which will require manually installing as well.
 I suggest just installing Anaconda from the start to avoid complications.

### search

Search provides a GUI program for searching GTR and downloading data. It utilizes the E-utilities.

### ngs

NGS is a hot topic in bioinformatics and genetic testing. These scripts provide some insight into 
the growth of NGS in the GTR and best practices for that data.