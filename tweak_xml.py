#!/usr/bin/env python

import os
import sys
import datetime
from lxml import etree

ERRORS = 0

def usage():
  print '''
     $ ./tweak_xml.py [-h | --help] path/to/pecan.xml
  
  '''

def verify_single_tag(tree, tag):
  global ERRORS
  if len(tree.findall(tag)) == 0:
    print "ERROR! Can't find {}".format(tag)
    ERRORS += 1
  elif len(tree.findall(tag)) > 1:
    print "ERROR! found more than one entry for tag: {}".format(tag)
    ERRORS += 1
  elif len(tree.findall(tag)) == 1:
    pass # Nothing to do, all ok


def get_element(tree, tag):
  if len(tree.findall(tag)) != 1:
    ERRORS += 1
    return None
  else:
    return tree.findall(tag)[0]




if __name__ == '__main__':

  if len(sys.argv) != 2:
    usage()
    sys.exit()

  OK_T0_WRITE = False
 
  in_pecan_xml = sys.argv[1] 

  tree = etree.parse(in_pecan_xml)
 
  verify_single_tag(tree, 'outdir')
  verify_single_tag(tree, 'info')
  verify_single_tag(tree, 'info/notes')
 
  get_element(tree, 'info/notes').text = "This file adjusted by the tweak_xml.py script"
  print "Set info/notes..."
  
  if tree.find('outdir').text != os.path.dirname(os.path.abspath(in_pecan_xml)):
    print "ERROR! Looks like the outdir setting does not agree with the pecan.xml file you are editing!!!"
    ERRORS += 1 

  if len(tree.findall('info/date')) == 0:
    for e in tree.findall('info'): # Should only be one item
      e.append(etree.Element('date'))
      print "Added info/date..."

  verify_single_tag(tree, 'info/date')

  # Now that we are sure the tag exists, modify it. 
  get_element(tree, 'info/date').text = datetime.datetime.now().isoformat()
  print "Set info/date..."

  get_element(tree, 'ensemble/size').text = '300'
  print "Set ensemble/size..."
  
  get_element(tree, 'ensemble/samplingspace/parameters/method').text = 'sobol'
  print "Set ensemble/samplingspace/parameters/method..."

  get_element(tree, 'model/dvmdostem_output_spec').text = '/data/tcarman/ngee_dhs_runs/custom_output_spec.csv' 
  print "Set model/dvmdostem_output_spec..."

  if ERRORS == 0:
    OK_TO_WRITE = True

  if OK_TO_WRITE:
    tree.write(in_pecan_xml, pretty_print=True, xml_declaration=True,   encoding="utf-8")
  else:
    print etree.tostring(tree, pretty_print=True, xml_declaration=True,   encoding="utf-8")
    print ""
    print "Something is eff'd up wiht the xml..."



  #from IPython import embed; embed()


 
