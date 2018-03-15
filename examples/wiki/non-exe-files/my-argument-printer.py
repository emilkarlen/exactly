import sys

for idx, argument in enumerate(sys.argv[1:]):
    print('Argument {}: {}'.format(idx + 1, argument))
