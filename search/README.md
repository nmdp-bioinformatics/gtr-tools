# GTR Search

gtr_search.py is a Python 2.7 program that provides a GUI for searching and downloading GTR data using the E-utilities.


### How to run this program

First, make sure you have followed the steps in the root [README](../README.md)

If you have the correct version of python, with all required modules, added to your system path
 (in environment variables (windows), .bashrc or .bash_profile (linux/osx))
  then you should be able to cd to the directory and enter `python gtr_search.py`

Issues may arise if you have multiple installations of Python. In that situation, I would suggest using a virtual
environment or else you need to specify the full path to the installation of python you want to use
 or prepend/replace in path so it runs the required version first.

Here are some resources if you need help with executing python programs:

* [Python on Windows](https://docs.python.org/2/faq/windows.html)
* [Python on Macintosh](https://docs.python.org/2/using/mac.html)
* [Python on Unix](https://docs.python.org/2/using/unix.html])

### Instructions

Instructions are also included in the 'Help' tab of the program.

There are three main types of searches (Test, Lab, Term) that are currently offered in four options:

* Search by Test ID
* Search by Lab ID
* Search by Gene ID
* Search by Gene Symbol or Name

Search by Test ID and Lab ID will provide the name of the test or lab if found, and offers the option to download the
xml data for the result.

Search by gene produces test IDs that are related to the search. By default, the program will provide the number of
 results found. An option to display up to the first 20 results to the program's console is available as 'return some',
 and an option to download a list of all the IDs is available as 'download all'.

#### Screenshots:

##### Windows (Windows 7)
![GUI Screenshot on Windows](../images/search_gtr_screenshot.png)

##### Linux (Linux Mint 17.2 'Rafaela' Cinnamon)
![GUI Screenshot on Linux Mint 17.2](../images/search_gtr_screenshot_linuxmint.png)

#### Flow Diagram:

![Program Flow Diagram](../images/search_gtr_flow.png)