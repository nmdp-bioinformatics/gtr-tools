# ngs

There are a handful of scripts in this directory that provide some insight into the Next-Generation (NGS) / 
Massively-Parallel (MPS) Sequencing used in genetic testing. They work with the data in the NIH Genetic
 Testing Registry (GTR) to gain some insight into the growth and standards of this methodology.

### How to run these programs

First, make sure you have followed the steps in the root [README](../README.md)

If you have the correct version of python, with all required modules, added to your system path
 (in environment variables (windows), .bashrc or .bash_profile (linux/osx))
  then you should be able to cd to the directory and enter `python [program_name.py]`

Issues may arise if you have multiple installations of Python. In that situation, I would suggest using a virtual
environment or else you need to specify the full path to the installation of python you want to use
 or prepend/replace in path so it runs the required version first.

Here are some resources if you need help with executing python programs:

* [Python on Windows](https://docs.python.org/2/faq/windows.html)
* [Python on Macintosh](https://docs.python.org/2/using/mac.html)
* [Python on Unix](https://docs.python.org/2/using/unix.html])

### About

##### GTR_NGS.py

This program will find the most recent data-set from GTR, parse out to a new xml file with just NGS tests and their labs,
and return a summary of the number of tests and labs with NGS tests out of the total number of tests and labs in GTR.

output:  

* gtr_data.xml
* GTR_NGS.xml
* GTR_NGS_COUNTS.txt

##### TOPNGS.py

This program will run GTR_NGS.py to produce the truncated xml file if the most recent file does not exist already.
 It will then identify labs that provide NGS testing with high-quality documentation. It will print the lab and test
 IDs to the console and save a file of the raw xml data for these labs and tests.
 
output:  

* ngs_high_detail.xml

##### NGS_STATS.py

This program will dig through the archival data at GTR to track the growth of NGS testing stored in the registry.
It then generates some plots to visualize these trends.

output:

* NGS_tests_by_count.jpg
* NGS_labs_by_count.jpg
* NGS_tests_by_percent.jpg
* NGS_labs_percent.jpg