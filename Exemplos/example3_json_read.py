#!/usr/bin/env python

import os
import sys
import json

def usage():
    print
    print("### Usage:   ",os.path.basename(sys.argv[0])," <json file>")
    print
    sys.exit()

def main():

    if len(sys.argv) < 2:
        usage()

    with open(sys.argv[1], 'r') as fIN:
        a = json.load(fIN)
        print(a)
        print(a["parameter2"])

if __name__=="__main__":
    main()
