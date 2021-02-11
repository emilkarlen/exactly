import os
import sys

expected_value = sys.argv[2]

actual_value = os.environ[sys.argv[1]]

if expected_value == actual_value:
    sys.exit(0)
else:
    sys.stderr.write(
        'Expected: {}\nFound   : {}\n'.format(
            expected_value,
            actual_value,
        )
    )
    sys.exit(1)
