import unittest

from exactly_lib_test.util.file_utils import tmp_file_spaces, ensure_file_existence


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ensure_file_existence.suite(),
        tmp_file_spaces.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
