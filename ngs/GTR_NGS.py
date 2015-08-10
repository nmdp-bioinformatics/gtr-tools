#! /usr/bin/env python2.7
# Copyright 2015 National Marrow Donor Program (NMDP)
#
# This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
__author__ = 'mneylon'

# imports
from ftplib import FTP
import gzip
import os
from lxml import etree as ET
import fnmatch

gtr_data = "gtr_data.xml"
ngs_only = "GTR_NGS.xml"
ngs_counts = 'GTR_NGS_COUNTS.txt'


def get_new_data():
    ncbi_ftp = "ftp.ncbi.nlm.nih.gov"
    gtr_data_dir = "pub/GTR/data/"
    filename = 'gtr_ftp.xml.gz'

    # FTP file download
    try:
        ftp = FTP(ncbi_ftp)  # making initial connection to ftp server
        ftp.login()  # anonymous login, no password - publicly available
        ftp.cwd(gtr_data_dir)  # changing directory to where gtr data is

        # finds the lsat modified date of the file
        modified_time = ftp.sendcmd('MDTM ' + filename)
        modified_time = modified_time[4:]



        # finds the last file we downloaded
        flag = False
        newest_file = ''
        for file in os.listdir('.'):
            y = file[8:-7]
            if y == modified_time:
                flag = True
                newest_file = file
                break

        # compares the date modified for the old file and current file on server
        # if a new file is found, downloads and extracts, else it does nothing.
        if flag == False:
            outfile = 'gtr_ftp_' + modified_time + '.xml.gz'
            ftp.retrbinary('RETR gtr_ftp.xml.gz', open(outfile, 'wb').write)  # retrieving and downloading file
            ftp.quit()  # closing ftp connection

            ##decompressing gzip and saving to new file
            f = gzip.open(outfile, 'rb')  # opening compressed file
            with open(gtr_data, 'wb') as g:  # opening new outfile to write decompressed file to
                g.write(f.read())  # reading uncompressed stream into write of new file
            f.close()  # closing connection to the open compressed file
            print "A new file has been found on the server, downloaded, and extracted to 'gtr_data.xml'\n"
            return True
        else:
            print "No new file on the server"
            return False

        # deleting original compressed file
        # os.remove('gtr_ftp.xml.gz')

    except Exception, e:
        print str(e)

def check_for_file():
    """Checks for final output, in case no new data is needed to update it."""
    flag = False
    for file in os.listdir('.'):
        if file == 'GTR_NGS.xml':
            flag = True
            break
    return flag

def check_for_summary():
    flag = False
    for file in os.listdir('.'):
        if file == ngs_counts:
            flag = True
            break
    return flag


# quickly finds labs with HLA testing and creates a short xml file
def iterparsing():
    """Find tests with NGS methodology.
    :return:
    """
    header = '<?xml version="1.0" encoding="utf-8"?>'
    root = '<GTRPublicData Version="1.0">'
    foot = '</GTRPublicData>'

    with open(ngs_only, 'wb') as f:
        f.write(header)
        f.write("\n")
        f.write(root)
        f.write("\n")

    events = ("start","end")
    tree = ET.iterparse(gtr_data, tag='GTRLabData') # sets up iterparse with labdata tags as root elements

    lab_count = 0
    ngs_lab_count = 0
    test_count = 0
    NGS_test_count = 0

    for event, element in tree: # traverses elements at labdata level


        lab_count += 1
        flag = False # set to false to start, true when that lab has HLA testing
        lab_info = ""
        test_info = ""
        for child in element: #looking at deeper levels within each lab

            if child.tag == 'GTRLab': #finding lab info
                lab_info = ET.tostring(child, encoding='UTF-8')

            if child.tag == ('GTRLabTest' or 'GTRLabResearchTest'): #finding tests and reporting any that test HLA
                test_count += 1
                if "Next-Generation (NGS)/Massively parallel sequencing (MPS)" in ET.tostring(child, encoding='UTF-8'):
                    test_info += ET.tostring(child, encoding='UTF-8')
                    NGS_test_count += 1
                    flag = True

        if flag == True: # writing out lab and its HLA tests to new file
            ngs_lab_count += 1
            lab_info += test_info
            with open(ngs_only, 'a+') as f:
                f.write("<GTRLabData>\n")
                f.write(lab_info)
                f.write("\n</GTRLabData>\n")

        element.clear() #frees previous content from memory

    with open(ngs_only, 'a+') as f:
        f.write(foot)

    print "{} labs with NGS tests out of {} total labs.\n {} NGS tests out of {} total tests".format(ngs_lab_count, lab_count, NGS_test_count, test_count)
    print "Find file with relevant labs and tests output to GTR_NGS.xml"

    with open(ngs_counts, 'w') as f:
        f.write('total_labs\ttotal_tests\tngs_labs\tngs_tests\n')
        f.write(str(lab_count) + '\t' + str(test_count)+'\t'+str(ngs_lab_count)+'\t'+str(NGS_test_count))

def print_summary():
    with open(ngs_counts, 'r') as f:
        x = f.readlines()
        stats = x[1].split('\t')
        total_labs = stats[0]
        total_tests = stats[1]
        ngs_labs = stats[2]
        ngs_tests = stats[3]
        print "{} labs with NGS tests out of {} total labs.\n {} NGS tests out of {} total tests".format(ngs_labs, total_labs, ngs_tests, total_tests)
        print "Find file with relevant labs and tests output to GTR_NGS.xml"

def main():
    if get_new_data(): # if a new data-set is found
        iterparsing() # then parse it to find results, print, and save
    else: # if we already have the most recent data-set
        if check_for_file(): # check that we still have the final parsed file
            if check_for_summary(): # check that we still have the summary file from last time
                print_summary() # then print the summary file generated last time. NEED TO ADD CHECK FOR THIS TOO.
            else: # if we don't have the summary from last run
                iterparsing() # then parse again.
        else: # if we don't have the parsed out file, do it again
            iterparsing() # if the parsed file isn't there, parse it again.




if __name__ == '__main__':
    main()