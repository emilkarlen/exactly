import os
import sys

if sys.argv[1] in os.environ:
    sys.stderr.write('{} is present: {}'.format(
        sys.argv[1],
        os.environ[sys.argv[1]]
    )
    )
    sys.exit(1)
else:
    sys.exit(0)
