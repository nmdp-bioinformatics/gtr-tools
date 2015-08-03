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
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import csv

ngs_counts = "ngs_data.txt"

def get_data():
    """
    Check for and retrieve archived data from GTR.
    """
    ncbi_ftp = "ftp.ncbi.nlm.nih.gov"
    gtr_archive_data_dir = "pub/GTR/data/xml_archive"
    gtr_new_data_dir = "/pub/GTR/data"
    current_dat_filename = 'gtr_ftp.xml.gz'

    # FTP file download
    try:
        ftp = FTP(ncbi_ftp)  # making initial connection to ftp server
        ftp.login()  # anonymous login, no password - publicly available
        ftp.cwd(gtr_archive_data_dir)  # changing directory to where gtr archive data is

        gtr_filenames = ftp.nlst()

        local_filenames = []

        for local_file in os.listdir('.'):
            local_filenames.append(local_file)


        for file in gtr_filenames:
            if file in local_filenames:
                pass
            else:
                print "downloading file", file
                ftp.retrbinary('RETR ' + file, open(file, 'wb').write)

        ftp.cwd(gtr_new_data_dir)

        # finds the lsat modified date of the file
        modified_time = ftp.sendcmd('MDTM ' + current_dat_filename)
        modified_time = modified_time[4:-6]
        year = modified_time[0:4]
        month = modified_time[4:6]
        day = modified_time[6:8]
        modified_time = year + '_' + month + '_' + day



        #strips out the datetime modified of the last file that we saved in its name
        flag = False
        newest_file = ''
        for file in local_filenames:
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

            gtr_filenames.append(outfile)
            print "A new file has been found on the server. \n"
            return (gtr_filenames, True)
        else:
            print "No new file on the server."
            ftp.quit()
            gtr_filenames.append(newest_file)
            return (gtr_filenames, False)

    except Exception, e:
        print str(e)


def iterparsing(filename):
    """Find tests with NGS methodology.
    """

    events = ("start","end")
    tree = ET.iterparse(filename, tag='GTRLabData') # sets up iterparse with labdata tags as root elements

    lab_count = 0
    ngs_lab_count = 0
    test_count = 0
    NGS_test_count = 0

    for event, element in tree: # traverses elements at labdata level


        lab_count += 1
        flag = False # set to false to start, true when that lab/test has NGS testing
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

        if flag == True: # writing out lab and its ngs tests to new file
            ngs_lab_count += 1

        element.clear() #frees previous content from memory


    filetime = filename[8:-4]
    date_of_file = filetime.replace('_', '-')



    print "{} labs with NGS tests out of {} total labs.\n {} tests out of {} total tests for {}".format(ngs_lab_count, lab_count, NGS_test_count, test_count, filename)
    with open(ngs_counts, 'a+') as f:
        f.write(str(date_of_file) + "\t" + str(lab_count) + "\t" + str(test_count) + "\t" + str(ngs_lab_count) + "\t" + str(NGS_test_count) + "\n" )



def summary():
    """
    Finds summary results to generate report.
    """

    filenames, flag = get_data()
    if flag == True: # if there is new data found, will parse through it all, otherwise it will skip if we have the data already
        with open(ngs_counts, 'w') as f:
            f.write("Date\tTotal Labs\tTotal Tests\tNGS Labs\tNGS Tests\n")
        for file in filenames:
            outfile = file[:-3]
            f = gzip.open(file, 'rb')  # opening compressed file
            with open(outfile, 'wb') as g:  # opening new outfile to write decompressed file to
                g.write(f.read())  # reading uncompressed stream into write of new file
            f.close()  # closing connection to the open compressed file
            iterparsing(outfile)
            os.remove(outfile) # delete large file when complete with parsing
    else:
        pass

def plot():
    """Plot the growth of NGS in GTR over time."""

    summary() # first get final numbers, will refresh file if new data has been found

    print "Graphs of NGS tests and their labs are displayed and also saved in your pwd."

    test_count_data = [] # create lists to store date and NGS number
    test_percent_data = []
    lab_count_data = []
    lab_percent_data = []
    total_labs_data = []
    total_tests_data = []

    with open(ngs_counts, 'r') as f:
        reader = csv.reader(f, delimiter="\t")
        reader.next()
        for line in reader:
            date = line[0]
            lab_count = line[1]
            test_count = line[2]
            ngs_lab_count = line[3]
            NGS_test_count = line[4]


            test_count_data.append((date, NGS_test_count))
            lab_count_data.append((date, ngs_lab_count))

            test_percent = 100*(float(NGS_test_count)/float(test_count))
            lab_percent = 100*(float(ngs_lab_count)/float(lab_count))

            test_percent_data.append((date, test_percent))
            lab_percent_data.append((date, lab_percent))

            total_labs_data.append((date, lab_count))
            total_tests_data.append((date, test_count))


    x = [dates.datestr2num(date) for (date,value) in test_count_data]
    x_max = [dates.datestr2num(date) for (date,value) in total_tests_data]
    y_max = [value for (date,value) in total_tests_data ]
    y = [value for (date,value) in test_count_data]

    x_ngs_lab = [dates.datestr2num(date) for (date,value) in lab_count_data]
    y_ngs_lab = [value for (date,value) in lab_count_data]
    y_lab_max = [value for (date,value) in total_labs_data]

    x_ngs_test_percent = [dates.datestr2num(date) for (date,value) in test_percent_data]
    y_ngs_test_percent = [value for (date,value) in test_percent_data]

    x_ngs_lab_percent = [dates.datestr2num(date) for (date,value) in lab_percent_data]
    y_ngs_lab_percent = [value for (date,value) in lab_percent_data]

    ym = dates.DateFormatter('%Y-%m')

    fig = plt.figure()
    fig.suptitle('NGS Tests in GTR', fontsize=14, fontweight='bold')
    ax = fig.add_subplot(111)
    ax.plot(x,y, label='NGS Tests')
    ax.plot(x_max,y_max, label='Total Tests')
    ax.legend(loc='upper left')
    ax.xaxis.set_major_locator(dates.MonthLocator())
    ax.xaxis.set_major_formatter(ym)
    plt.xticks(rotation='vertical')
    plt.subplots_adjust(bottom=.3)
    ax.set_xlabel('Date')
    ax.set_ylabel('Tests')
    fig.savefig('NGS_tests_by_count.jpg')

    fig_labs = plt.figure()
    fig_labs.suptitle('Labs with NGS in GTR', fontsize=14, fontweight='bold')
    ax_labs = fig_labs.add_subplot(111)
    ax_labs.plot(x_ngs_lab,y_ngs_lab, label='Labs with NGS Tests')
    ax_labs.plot(x_ngs_lab,y_lab_max, label='Total Labs')
    ax_labs.legend(loc='upper left')
    ax_labs.xaxis.set_major_locator(dates.MonthLocator())
    ax_labs.xaxis.set_major_formatter(ym)
    plt.xticks(rotation='vertical')
    plt.subplots_adjust(bottom=.3)
    ax_labs.set_xlabel('Date')
    ax_labs.set_ylabel('Labs')
    fig_labs.savefig('NGS_labs_by_count.jpg')

    fig_test_percent = plt.figure()
    fig_test_percent.suptitle('Percent of Tests in GTR that are NGS', fontsize=14, fontweight='bold')
    ax_test_percent = fig_test_percent.add_subplot(111)
    ax_test_percent.plot(x_ngs_test_percent, y_ngs_test_percent)
    ax_test_percent.xaxis.set_major_locator(dates.MonthLocator())
    ax_test_percent.xaxis.set_major_formatter(ym)
    plt.xticks(rotation='vertical')
    plt.subplots_adjust(bottom=.3)
    ax_test_percent.set_xlabel('Date')
    ax_test_percent.set_ylabel('Percent of Tests')
    fig_test_percent.savefig('NGS_tests_by_percent.jpg')

    fig_lab_percent = plt.figure()
    fig_lab_percent.suptitle('Percent of Labs in GTR that have NGS tests', fontsize=14, fontweight='bold')
    ax_lab_percent = fig_lab_percent.add_subplot(111)
    ax_lab_percent.plot(x_ngs_lab_percent, y_ngs_lab_percent)
    ax_lab_percent.xaxis.set_major_locator(dates.MonthLocator())
    ax_lab_percent.xaxis.set_major_formatter(ym)
    plt.xticks(rotation='vertical')
    plt.subplots_adjust(bottom=.3)
    ax_lab_percent.set_xlabel('Date')
    ax_lab_percent.set_ylabel('Percent of Labs')
    fig_lab_percent.savefig('NGS_labs_by_percent.jpg')

    plt.show()

def main():
    plot()



if __name__ == '__main__':
    main()