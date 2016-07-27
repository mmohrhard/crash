#!/usr/bin/env python
from __future__ import print_function
import os
import re
import fileinput

def is_file_line(line):
    return line.startswith('FILE')

file_map = {}

current_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_dir, 'filemap'), 'r') as f:
    lines = f.readlines()
    for line in lines:
        split_line = line.split()
        file_map[split_line[0]] = split_line[1]

for line in fileinput.input(inplace=True):
    regexp = re.compile("(FILE \d+ )(.*)")
    if is_file_line(line):
        results = regexp.match(line)
        path = results.group(2)
        path = path.replace("c:\\cygwin64\\home\\buildslave\\source\\libo-core\\", "")
        if path in file_map:
            path = file_map[path]
        print("%s %s" % (results.group(1), path))
    else:
        print(line, end="")
