import sys

factor = int(sys.argv[1])

for i, s in enumerate(sys.stdin.readlines()):
    if i % factor == 0:
        sys.stdout.write(s)
