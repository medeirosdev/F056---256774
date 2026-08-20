#!/usr/bin/env python

import re

root_re = re.compile("(([^/]*\S+)\.root$)")
#root_re = re.compile("(?P<rootfile>([^/]*))\.root")
#root_re = re.compile("(?P<rootfile>(\S*))\.root")
#root_re = re.compile("(?P<rootfile>\S*\.root)")
#root_re = re.compile("(?P<path>\S+/)(?P<rootfile>([^/]*)\.root)")
#root_re = re.compile("(?P<path>\S*/*)(?P<rootfile>(\S+_m\d+\.root))")
#root_re = re.compile("\S*/*(?P<rootfile>(\S+_m(?P<path>\d+)\.root))")

file = "a/b/c_m676.root"
#file = "d_m11.root"
files = []
files.append(file)

for f in files:
    match = root_re.search(f)

    if match:
        print("re pattern      ",root_re.pattern)
        print("group 0         ",match.group(0))
        print("group 1         ",match.group(1))
        print("group 2         ",match.group(2))
        if "rootfile" in match.groupdict():
            print("group 'rootfile'",match.group("rootfile"))
        if "path" in match.groupdict():
            print("group 'path'    ",match.group("path"))
