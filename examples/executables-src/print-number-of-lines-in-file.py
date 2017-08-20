import os
import sys

if len(sys.argv) != 2:
    sys.stderr.write('Invalid usage.\nSyntax: FILE' + os.linesep)
    sys.exit(1)

file_name = sys.argv[1]

with open(file_name) as f:
    lines = f.readlines()

print(str(len(lines)))
