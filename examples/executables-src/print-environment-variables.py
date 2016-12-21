import os
import sys

for var_name in sys.argv:
    try:
        info = '= ' + os.environ[var_name]
    except KeyError:
        info = 'is undefined'
    print(var_name + ' ' + info)
