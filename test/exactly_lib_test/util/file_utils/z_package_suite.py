import unittest

from exactly_lib_test.util.file_utils import dir_file_spaces, ensure_file_existence, spooled_file


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ensure_file_existence.suite(),
        dir_file_spaces.suite(),
        spooled_file.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
