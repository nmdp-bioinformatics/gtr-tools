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
from lxml import etree
import time
import GTR_NGS

input = 'GTR_NGS.xml'

def find_detailed_NGS():
    """Find NGS tests/labs with high detail."""

    print "Looking for the best documented tests now..."
    labs = set()
    tests = set()

    tree = etree.iterparse(input)
    for event, element in tree:

        if (element.tag == 'MethodAdd'):

            for child in element:
                if child.tag == 'Protocol':

                    y = element.getroottree()
                    element_path = y.getpath(element)
                    splat = element_path.split("/")
                    splat = splat[1:]
                    splat_len = len(splat)
                    id_climb_count = splat_len

                    ele = element
                    for i in range(id_climb_count): # recursively climbing parent nodes
                        last_ele = ele.getparent()
                        ele = last_ele


                        if ele.tag == ('GTRLabTest' or 'GTRResearchLabTest'):
                            test_id = ele.get('id')
                            tests.add(test_id) # if typing test, finds the test id and adds to set

                        if ele.tag == 'GTRLabData':
                            for child in ele:
                                if child.tag == 'GTRLab':
                                    lab_id = child.get('id')
                                    labs.add(lab_id)
                            break
        # element.clear() # clears memory once it is done parsing this element.

    print "NGS Labs:",sorted(list(labs))
    print "NGS Tests:",sorted(list(tests))
    print "Number of labs with NGS tests that have protocol:", len(labs)
    print "Number of NGS tests with a protocol:", len(tests)
    return (list(tests),list(labs))

def output(tests, labs):
    """Create new xml with only high detailed NGS tests."""
    print "Saving the raw xml data for these tests and labs..."
    current_date = time.strftime("%m/%d/%Y")
    header = '<?xml version="1.0" encoding="UTF-8"?>'
    comment = '<!-- NGS Tests with highly detailed documentation; created '+current_date+' -->'
    root = '<GTRPublicData Version="1.0">'
    foot = '</GTRPublicData>'

    ngs_high_detail = 'ngs_high_detail.xml'

    with open(ngs_high_detail, 'wb') as f:
        f.write(header)
        f.write("\n")
        f.write(comment)
        f.write("\n")
        f.write(root)
        f.write("\n")

    def write_out(item):
        """Write out selected elements to new xml file."""
        with open(ngs_high_detail, 'a+') as f:
            f.write("<GTRLabData>\n")
            f.write(item)
            f.write("\n</GTRLabData>\n")

    tree = etree.iterparse(input, tag='GTRLabData')
    for event, element in tree:
        lab_tests = ""
        for child_element in element:
            if child_element.tag == 'GTRLab':
                if child_element.get('id') in labs:
                    lab_tests = etree.tostring(child_element, encoding='UTF-8')
            if child_element.tag == ('GTRLabTest' or 'GTRLabResearchTest'):
                if child_element.get('id') in tests:
                    lab_tests += etree.tostring(child_element, encoding='UTF-8')
        if lab_tests:
            write_out(lab_tests)
        element.clear()

    with open(ngs_high_detail, 'a') as f:
        f.write(foot)

    print "Full data of these labs and tests is output to a new xml file 'ngs_high_detail.xml'"


if __name__ == '__main__':
    GTR_NGS.main()
    tests,labs = find_detailed_NGS()
    output(tests, labs)