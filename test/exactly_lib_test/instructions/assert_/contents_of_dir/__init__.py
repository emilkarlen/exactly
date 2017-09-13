import unittest

from exactly_lib_test.instructions.assert_.contents_of_dir import common, empty, num_files


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        common.suite(),
        empty.suite(),
        num_files.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
