#! /usr/bin/env Python 2.7
__author__ = 'mneylon'
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

# imports
from urllib2 import *
from lxml import etree
from Tkinter import *
from ttk import *
import tkMessageBox
import threading
import Queue
import os
import errno

class retrieve:
    """Retrieve GTR data from search."""
    # (search type, search query, **kwargs )
    # search type: test, lab, term
    # query, anything

    # **kwargs:
    #   field, any field to search against
    #   id_list: some, all -- default, no argument, returns count, some and all returns the list of some or all IDs

    def __init__(self, search_type, query, **kwargs):
        self.search_type = search_type
        self.query = query
        self.labtestoption = ''
        for name, value in kwargs.items():
            if name == 'field':
                self.field = value
            elif name == 'id_list':
                self.id_list = value
            elif name == 'labtestoption':
                self.labtestoption = value
            else:
                result = name, "is not a valid argument.\n"
                submit_to_tkinter(result)
        if self.search_type == 'test':
            self.test_search()
        elif self.search_type == 'lab':
            self.lab_search()
        elif self.search_type == 'term':
            self.term_search()
        else:
            result = "Invalid test type. Please enter 'test','lab',or 'term' as first argument.\n"
            submit_to_tkinter(result)

    def test_search(self):
        """Search for tests, by test id."""
        base = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gtr&rettype=gtracc&id="
        request = base + str(self.query)
        response = urlopen(request).read()
        filename = self.query + '.xml'
        tree = etree.fromstring(response)
        test_name = ''
        for root in tree:
            for labtest in root:
                for element in labtest:
                    if element.tag == 'TestName':
                        test_name = element.text
        prettytree = etree.tostring(tree, pretty_print=True)
        if test_name:
            if self.labtestoption == 'download':
                with open(download_directory +'/' + filename, 'w') as f:
                    f.write(prettytree)
                result = "Found test " + self.query + ": " + str(test_name) +". Downloaded to " + filename + "\n"
                submit_to_tkinter(result)
                return None # not actually returning object back to thread call,
                # sending over to Queue, so need to return None so thread exits
            else:
                result = "Found test " + self.query + ": " + str(test_name) +". Select 'download' on the bottom left to save this data.\n"
                submit_to_tkinter(result)
                return None
        else:
            result = "Sorry, could not find test '" +  self.query + "'. Please try another search.\n"
            submit_to_tkinter(result)
            return None

    def lab_search(self):
        """Retrieve lab data."""
        # this one is a bit of a hack, efetch not enabled for lab yet
        base1 = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=orgtrack&id="
        request1 = base1 + str(self.query)
        response1 = urlopen(request1).read()
        tree = etree.fromstring(response1)
        self.lab_name = ''
        for root in tree:
            for ele in root:
                if ele.tag == 'DocumentSummary':
                    for element in ele:
                        if element.tag == 'TITLE':
                            self.lab_name = element.text
        if self.lab_name:
            if self.labtestoption == '' or self.labtestoption == 'name':
                result = "Found lab " + self.query + ": " + self.lab_name + ". Select 'download' on the bottom left to save this data.\n"
                submit_to_tkinter(result)
                return None
            elif self.labtestoption == 'download':
                base2 = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gtr&term="
                request2 = base2 + str(self.query)  + '[All%20Fields]'
                self.initial_response = urlopen(request2).read()
                tree2 = etree.fromstring(self.initial_response)
                some_ids = []
                for element in tree2:
                    if element.tag == 'IdList':
                        for child in element:
                            some_ids.append(child.text)
                filename = self.query + '.xml'
                for item in some_ids:
                    base3 = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gtr&rettype=gtracc&id="
                    request3 = base3 + str(item)
                    response3 = urlopen(request3).read()
                    tree3 = etree.fromstring(response3)
                    flag = False # flagged True if the correct data is found
                    for root in tree3:
                        for labtest in root:
                            if labtest.tag == 'GTRLab':
                                if labtest.get('id') == str(self.query):
                                    flag = True
                                    for root in tree3:
                                        for labtest in root:
                                            if labtest.tag == 'GTRLab':
                                                x = etree.tostring(labtest, encoding='UTF-8')
                                                with open(download_directory +'/' + filename, 'w') as f:
                                                    f.write(x)
                                                result = "Found lab " + self.query + ": " + self.lab_name + ". Downloaded to '" + filename + "'\n"
                                                submit_to_tkinter(result)
                                                return None
                                    break
                    if flag:
                        break
        else:
            result = "Could not find lab '" + self.query + "'. Please try searching again, or use the term search.\n"
            submit_to_tkinter(result)
            return None

    def term_search(self):
        """Search for tests by term."""
        base = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gtr&term="
        request = base + str(self.query)
        try:
            request += '[' + str(self.field) + ']'
        except:
            pass
        self.initial_response = urlopen(request).read()
        tree = etree.fromstring(self.initial_response)
        for element in tree:
            # print element.tag, element.text
            if element.tag == 'Count':
                self.result_count = int(element.text)
                try:
                    self.get_all_ids()
                    self.get_some_ids()
                except:
                    if self.result_count > 0:
                        result = "There are " + str(self.result_count) + " results for your search. Please specify how you want to retrieve the results by selecting a return method on the bottom left.\n"
                        submit_to_tkinter(result)
                        return None
                    else:
                        result = "No results. Please try a different search.\n"
                        submit_to_tkinter(result)
                        return None

    def get_all_ids(self):
        """Need to find count in term search first, then pass to here to return all IDs."""
        if self.id_list.lower() == 'all':
            base = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gtr&term="
            request = base + str(self.query)
            try:
                request += '[' + str(self.field) + ']'
                request += '&retmax=' + str(self.result_count)
            except:
                pass
            response = urlopen(request).read()
            tree = etree.fromstring(response)
            all_ids = []
            filename = self.query + 'results.txt'
            for element in tree:
                # print element.tag
                if element.tag == 'IdList':
                    for child in element:
                        all_ids.append(child.text)
            if self.result_count < 1:
                result = "Sorry, no results for that search. Try again.\n"
                submit_to_tkinter(result)
                return None
            else:
                with open(download_directory +'/' + filename, 'w') as f:
                    f.write('Test_ID\n')
                    for item in all_ids:
                        f.write(str(item) + '\n')
                result = str(self.result_count) + " results, saved to '" + filename + "'\n"
                submit_to_tkinter(result)
                return None

    def get_some_ids(self):
        """Return the first few example responses."""
        if self.id_list.lower() == 'some':
            tree = etree.fromstring(self.initial_response)
            some_ids = []
            for element in tree:
                if element.tag == 'IdList':
                    for child in element:
                        some_ids.append(child.text)
            if self.result_count > 0:
                result = str(self.result_count) + ' results. Here are a few of them as an example:\n' + str(some_ids) + "\nRetrieve all by selecting 'Download all' on the bottom left\n"
                submit_to_tkinter(result)
                return None
            else:
                result = "Sorry, no results for that search. Please try a different search.\n"
                submit_to_tkinter(result)
                return None
    def wildcard(self):
        """Search with any input."""
        pass


license_text = """                   GNU LESSER GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.


  This version of the GNU Lesser General Public License incorporates
the terms and conditions of version 3 of the GNU General Public
License, supplemented by the additional permissions listed below.

  0. Additional Definitions.

  As used herein, "this License" refers to version 3 of the GNU Lesser
General Public License, and the "GNU GPL" refers to version 3 of the GNU
General Public License.

  "The Library" refers to a covered work governed by this License,
other than an Application or a Combined Work as defined below.

  An "Application" is any work that makes use of an interface provided
by the Library, but which is not otherwise based on the Library.
Defining a subclass of a class defined by the Library is deemed a mode
of using an interface provided by the Library.

  A "Combined Work" is a work produced by combining or linking an
Application with the Library.  The particular version of the Library
with which the Combined Work was made is also called the "Linked
Version".

  The "Minimal Corresponding Source" for a Combined Work means the
Corresponding Source for the Combined Work, excluding any source code
for portions of the Combined Work that, considered in isolation, are
based on the Application, and not on the Linked Version.

  The "Corresponding Application Code" for a Combined Work means the
object code and/or source code for the Application, including any data
and utility programs needed for reproducing the Combined Work from the
Application, but excluding the System Libraries of the Combined Work.

  1. Exception to Section 3 of the GNU GPL.

  You may convey a covered work under sections 3 and 4 of this License
without being bound by section 3 of the GNU GPL.

  2. Conveying Modified Versions.

  If you modify a copy of the Library, and, in your modifications, a
facility refers to a function or data to be supplied by an Application
that uses the facility (other than as an argument passed when the
facility is invoked), then you may convey a copy of the modified
version:

   a) under this License, provided that you make a good faith effort to
   ensure that, in the event an Application does not supply the
   function or data, the facility still operates, and performs
   whatever part of its purpose remains meaningful, or

   b) under the GNU GPL, with none of the additional permissions of
   this License applicable to that copy.

  3. Object Code Incorporating Material from Library Header Files.

  The object code form of an Application may incorporate material from
a header file that is part of the Library.  You may convey such object
code under terms of your choice, provided that, if the incorporated
material is not limited to numerical parameters, data structure
layouts and accessors, or small macros, inline functions and templates
(ten or fewer lines in length), you do both of the following:

   a) Give prominent notice with each copy of the object code that the
   Library is used in it and that the Library and its use are
   covered by this License.

   b) Accompany the object code with a copy of the GNU GPL and this license
   document.

  4. Combined Works.

  You may convey a Combined Work under terms of your choice that,
taken together, effectively do not restrict modification of the
portions of the Library contained in the Combined Work and reverse
engineering for debugging such modifications, if you also do each of
the following:

   a) Give prominent notice with each copy of the Combined Work that
   the Library is used in it and that the Library and its use are
   covered by this License.

   b) Accompany the Combined Work with a copy of the GNU GPL and this license
   document.

   c) For a Combined Work that displays copyright notices during
   execution, include the copyright notice for the Library among
   these notices, as well as a reference directing the user to the
   copies of the GNU GPL and this license document.

   d) Do one of the following:

       0) Convey the Minimal Corresponding Source under the terms of this
       License, and the Corresponding Application Code in a form
       suitable for, and under terms that permit, the user to
       recombine or relink the Application with a modified version of
       the Linked Version to produce a modified Combined Work, in the
       manner specified by section 6 of the GNU GPL for conveying
       Corresponding Source.

       1) Use a suitable shared library mechanism for linking with the
       Library.  A suitable mechanism is one that (a) uses at run time
       a copy of the Library already present on the user's computer
       system, and (b) will operate properly with a modified version
       of the Library that is interface-compatible with the Linked
       Version.

   e) Provide Installation Information, but only if you would otherwise
   be required to provide such information under section 6 of the
   GNU GPL, and only to the extent that such information is
   necessary to install and execute a modified version of the
   Combined Work produced by recombining or relinking the
   Application with a modified version of the Linked Version. (If
   you use option 4d0, the Installation Information must accompany
   the Minimal Corresponding Source and Corresponding Application
   Code. If you use option 4d1, you must provide the Installation
   Information in the manner specified by section 6 of the GNU GPL
   for conveying Corresponding Source.)

  5. Combined Libraries.

  You may place library facilities that are a work based on the
Library side by side in a single library together with other library
facilities that are not Applications and are not covered by this
License, and convey such a combined library under terms of your
choice, if you do both of the following:

   a) Accompany the combined library with a copy of the same work based
   on the Library, uncombined with any other library facilities,
   conveyed under the terms of this License.

   b) Give prominent notice with the combined library that part of it
   is a work based on the Library, and explaining where to find the
   accompanying uncombined form of the same work.

  6. Revised Versions of the GNU Lesser General Public License.

  The Free Software Foundation may publish revised and/or new versions
of the GNU Lesser General Public License from time to time. Such new
versions will be similar in spirit to the present version, but may
differ in detail to address new problems or concerns.

  Each version is given a distinguishing version number. If the
Library as you received it specifies that a certain numbered version
of the GNU Lesser General Public License "or any later version"
applies to it, you have the option of following the terms and
conditions either of that published version or of any later version
published by the Free Software Foundation. If the Library as you
received it does not specify a version number of the GNU Lesser
General Public License, you may choose any version of the GNU Lesser
General Public License ever published by the Free Software Foundation.

  If the Library as you received it specifies that a proxy can decide
whether future versions of the GNU Lesser General Public License shall
apply, that proxy's public statement of acceptance of any version is
permanent authorization for you to choose that version for the
Library."""

help_page = """                                  Instructions
Search by Test ID:
    Enter a GTR Accession ID for a test. This does not include 'GTR' or
    the preceding '0's.
        example: 23657
    Return options:
        Name (default):
            The default option will return the test name if found.
        Download:
            If download is selected, the test xml data will be saved to
            /search_downloads.

Search by Lab ID:
    Enter a GTR Accession ID for a lab. This does not include 'GTR' or
    the preceding '0's.
        example: 1027
    Return options:
        Name (default):
            The default option will return the lab name if found.
        Download:
            If download is selected, the lab xml data will be saved to
            /search_downloads.

Search by Gene ID:
    Enter an Entrez Gene ID.
        example: 672
    Return options:
        Count (default):
            The default option will return the number of tests that contain
            the searched Gene ID.
        Some:
            Selecting to return some will take the initial response, of up to
            20 Test IDs, and display them on the console.
        Download All:
            If download all is selected, all the Test IDs will be saved
            to a csv file in /search_downloads.

Search by Gene Name or Symbol:
    Enter an (HGNC) Official Symbol or Name.
        symbol example: BRCA2
        name example: Breast Cancer 2, early onset
    Return options:
        Count (default):
            The default option will return the number of tests that contain
            the searched Gene Symbol.
        Some:
            Selecting to return some will take the initial response, of up to
            20 Test IDs, and display them on the console.
        Download All:
            If download all is selected, all the Test IDs will be saved
            to a csv file in /search_downloads.
"""

request_queue = Queue.Queue()
result_queue = Queue.Queue()

def submit_to_tkinter(result):
    request_queue.put((result))
    return result_queue.get()

root = None
def mainthread():
    """Sets the gui on the main thread with a queue checker looping."""
    global root

    def timertick():
        """Checks the queue every half second."""
        try:
            result = request_queue.get_nowait()
            tex.insert(END, result)
            tex.see(END)
        except Queue.Empty:
            pass
        else:
            retval = result
            result_queue.put(retval)
        root.after(500, timertick)

    root = Tk()
    root.title('Search the Genetic Testing Registry')

    def about():
        """Popup license text."""
        top = Toplevel()
        scroll = Scrollbar(top)
        scroll.pack(side=RIGHT, fill=Y)
        top.title('About copying')
        msg = Text(top, yscrollcommand=scroll.set)
        msg.insert(END, license_text)
        msg.pack()
        msg.config(state='disabled')
        scroll.config(command=msg.yview)
        close_button = Button(top, text='Okay', command=top.destroy)
        close_button.pack()

    def help():
        """Popup instructions."""
        top = Toplevel()
        scroll = Scrollbar(top)
        scroll.pack(side=RIGHT, fill=Y)
        top.title('Help')
        msg = Text(top, yscrollcommand=scroll.set)
        msg.insert(END, help_page)
        msg.pack()
        msg.config(state='disabled')
        scroll.config(command=msg.yview)
        close_button = Button(top, text='Okay', command=top.destroy)
        close_button.pack()

    menubar = Menu(root)
    menubar.add_command(label='About', command=about)
    menubar.add_command(label='Help', command=help)
    root.config(menu=menubar)

    tex = Text(master=root) # main gui text console
    tex.pack(side=RIGHT)

    introduction = ("GTR Search  Copyright (C) 2015  National Marrow Donor Program (NMDP)\n"
                    "This program comes with ABSOLUTELY NO WARRANTY.\n"
                    "This is free software, and you are welcome to redistribute it\n"
                    "under certain conditions; click `about' for details.\n\n"
                    "This program will quickly identify your search and "
                     "serialize the results into a truncated xml file that is easier to view.\n"
                    "Results from data downloads are saved within /search_downloads\n"
                    "------------------------------\n")
    tex.insert(END, introduction)
    label = Label(root, text='Enter Search Term:')
    user_input = Entry(root)
    submit = Button(root, text="Search", command= lambda: execute())

    options = [
        'Select a search method',
        'Search by Test ID',
        'Search by Lab ID',
        'Search by Gene ID',
        'Search by Gene Symbol/Name']

    search_type = StringVar(root)
    search_type.set(options[0])
    select_search = apply(OptionMenu, (root, search_type) + tuple(options))
    select_search.pack()

    search_list_options = [
        'Select optional return method',
        'Return count',
        'Return some',
        'Download all'
    ]
    return_option = StringVar(root)
    return_option.set(search_list_options[0])
    list_download_options = apply(OptionMenu, (root, return_option) + tuple(search_list_options))

    lab_test_options = [
        'Select option',
        'Return name',
        'Download'
    ]
    lab_test_return_choice = StringVar(root)
    lab_test_return_choice.set(lab_test_options[0])
    lab_test_dropdown = apply(OptionMenu, (root, lab_test_return_choice) + tuple(lab_test_options))

    def check_type(*args):
        selected = search_type.get()
        try:
            list_download_options.pack_forget()
            lab_test_dropdown.pack_forget()
        except:
            pass
        if selected == options[3] or selected == options[4]:
            list_download_options.pack()
        elif selected == options[1] or selected == options[2]:
            lab_test_dropdown.pack()

    search_type.trace('w',check_type) # responds to search type change

    def execute():
        if search_type.get() == options[0]:
            tex.insert(END, 'Please select a search type\n')
            tex.see(END)
        elif search_type.get() == options[1]:
            id = user_input.get().strip()
            wait_a_sec_test(id)
        elif search_type.get() == options[2]:
            id = user_input.get().strip()
            wait_a_sec_lab(id)
        elif search_type.get() == options[3]:
            id = user_input.get().strip()
            wait_a_sec_gene_id(id)
        elif search_type.get() == options[4]:
            id = user_input.get().strip()
            wait_a_sec_gene_sym(id)

    def convert_optional_return_selection():
        return_method = return_option.get()
        if return_method == search_list_options[0] or return_method == search_list_options[1]:
            return 'count'
        elif return_method == search_list_options[2]:
            return 'some'
        elif return_method == search_list_options[3]:
            return 'all'

    def convert_labtest_return_selection():
        """Take selection and return appropriate argument to pass to the search."""
        return_method = lab_test_return_choice.get()
        if return_method == lab_test_options[0] or return_method == lab_test_options[1]:
            return 'name'
        elif return_method ==lab_test_options[2]:
            return 'download'

    def wait_a_sec_test(id):
        if id.isdigit():
            tex.insert(END,"Searching for test '{}', please wait...\n".format(id))
            tex.see(END)
            return_method = convert_labtest_return_selection()
            get_test_results(id, return_method)
        else:
            tex.insert(END,'Please enter a number\n')
            tex.see(END)

    def wait_a_sec_lab(id):
        if id.isdigit():
            tex.insert(END,"Searching for lab '{}', please wait...\n".format(id))
            tex.see(END)
            return_method = convert_labtest_return_selection()
            get_lab_results(id, return_method)
        else:
            tex.insert(END,'Please enter a number\n')
            tex.see(END)

    def wait_a_sec_gene_id(id):
        if id.isdigit():
            tex.insert(END,"Searching for tests with Gene ID '{}', please wait...\n".format(id))
            tex.see(END)
            return_method = convert_optional_return_selection()
            get_gene_id_results(id, return_method)
        else:
            tex.insert(END,'Please enter a number\n')
            tex.see(END)
    def wait_a_sec_gene_sym(id):
        if id:
            tex.insert(END,"Searching for tests for '{}', please wait...\n".format(id))
            tex.see(END)
            return_method = convert_optional_return_selection()
            get_gene_sym_result(id, return_method)
        else:
            tex.insert(END,'Please enter a gene name or symbol\n')
            tex.see(END)

    def kill():
        if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"): # checks before closing
            root.destroy()
    exit = Button(root, text='Exit', command=kill)
    root.protocol('WM_DELETE_WINDOW', kill) # calls kill definition when the windows event manager is used to exit

    label.pack()
    user_input.pack()
    submit.pack()
    exit.pack()
    timertick()

    root.mainloop()

# these functions pass off the user input to a new thread, so that the gui does not freeze in its loop
# while waiting for a response. This also means multiple searches can be made at the same time, but this is not
# advised. The results are then sent back to another function that loads them into the queue for the gui to read from.

def get_test_results(user_input, return_method):
    x = threading.Thread(target=retrieve, args=('test', user_input), kwargs={'labtestoption':return_method})
    x.daemon = True # shuts the program down if any of these threads are the only ones open (i.e. close main thread/gui while this is running).
    x.start()

def get_lab_results(user_input, return_method):
    x = threading.Thread(target=retrieve, args=('lab', user_input), kwargs={'labtestoption':return_method})
    x.daemon = True # shuts the program down if any of these threads are the only ones open (i.e. close main thread/gui while this is running).
    x.start()

def get_gene_id_results(user_input, return_method):
    if return_method == 'count':
        x = threading.Thread(target=retrieve, args=('term', user_input), kwargs={'field':'geneid'})
        x.daemon = True
        x.start()
    else:
        x = threading.Thread(target=retrieve, args=('term', user_input), kwargs={'field':'geneid','id_list':return_method})
        x.daemon = True
        x.start()

def get_gene_sym_result(user_input, return_method):
    if return_method == 'count':
        x = threading.Thread(target=retrieve, args=('term', user_input), kwargs={'field':'gene'})
        x.daemon = True
        x.start()
    else:
        x = threading.Thread(target=retrieve, args=('term', user_input), kwargs={'field':'gene','id_list':return_method})
        x.daemon = True
        x.start()

download_directory = 'search_downloads'
def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

if __name__ == '__main__':
    make_sure_path_exists(download_directory)
    mainthread()