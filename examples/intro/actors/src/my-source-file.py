import sys

print('I am a source file')

args = sys.argv[1:]
if args:
    print('')
    print('I was given')
    for arg in args:
        print(' * ' + arg)
