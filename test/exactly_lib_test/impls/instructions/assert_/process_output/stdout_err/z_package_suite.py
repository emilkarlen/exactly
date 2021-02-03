import unittest

from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err import stderr, stdout


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        stdout.suite(),
        stderr.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
