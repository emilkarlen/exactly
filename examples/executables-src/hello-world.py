import os
import sys
from typing import TextIO


def output_to(of: TextIO):
    of.write('Hello, World!')
    of.write(os.linesep)


if len(sys.argv) == 3:
    if sys.argv[1] != '-o':
        sys.exit(1)
    with open(sys.argv[2], 'w') as f:
        output_to(f)
elif len(sys.argv) != 1:
    sys.exit(1)
else:
    output_to(sys.stdout)
