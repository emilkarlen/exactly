import sys

for arg in sys.argv[1:]:
    sys.stderr.write(arg)
    sys.stderr.write('\n')

sys.exit(1)
