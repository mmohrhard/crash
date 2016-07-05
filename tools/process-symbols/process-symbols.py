#!/usr/bin/env python
from __future__ import print_function
import fileinput

def is_file_line(line):
    return line.startswith('FILE')

file_map = {}

with open('filemap', 'r') as f:
    lines = f.readlines()
    for line in lines:
        split_line = line.split()
        file_map[split_line[0]] = split_line[1]

for line in fileinput.input(inplace=True, backup='.bak'):
    if is_file_line(line):
        split = line.split()
        path = split[2]
        path = path.replace("c:\\cygwin64\\home\\buildslave\\source\\libo-core\\", "")
        if path in file_map:
            path = file_map[path]
        print("%s %s %s" % (split[0], split[1], path))
    else:
        print(line, end="")
