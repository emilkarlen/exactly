import os
import sys

var_name = sys.argv[1]

if var_name in os.environ:
    sys.stdout.write(os.environ[var_name])
