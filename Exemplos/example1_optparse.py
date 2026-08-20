#!/usr/bin/env python

import os
import sys

from optparse import OptionParser

# try example1_optparse.py -h

def main():

    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option("-p","--par", dest="parameter", default=False, action="store_true",
                      help="Flag to test parameter passing [default: False]")

    (opts, args) = parser.parse_args()

    if opts.parameter:
        print("Parameter value True")
    else:
        print("Parameter value False")

if __name__=="__main__":
    main()
