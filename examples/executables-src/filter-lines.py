import os
import sys

if len(sys.argv) != 2:
    sys.stderr.write('Invalid usage.\nSyntax: STRING' + os.linesep)
    sys.exit(1)

text_to_find = sys.argv[1]

for line in sys.stdin.readlines():
    if text_to_find in line:
        sys.stdout.write(line)
