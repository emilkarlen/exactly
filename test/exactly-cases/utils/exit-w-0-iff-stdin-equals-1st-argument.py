import sys

expected = sys.argv[1]

actual = sys.stdin.read()

if expected == actual:
    sys.exit(0)
else:
    sys.stderr.write('\n'.join([
        'Expected: ' + repr(expected),
        'Actual  : ' + repr(actual),
    ]))
    sys.stderr.write('\n')
    sys.exit(1)
