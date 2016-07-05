#!/usr/bin/env python
from __future__ import print_function
import fileinput

VALID_EXTENSIONS = set([ 'cxx', "cpp", "hxx", "hpp", "h", "c", "cc", "hh" ])

def is_source_file(line):
    ext = line.rpartition(".")
    if ext[2] in VALID_EXTENSIONS:
        return True

    return False

for line in fileinput.input(inplace=True, backup='.bak'):
    line = line.strip()
    if is_source_file(line):
        ms_file = line.lower().replace("/", "\\")
        print("%s %s" % (ms_file, line))
