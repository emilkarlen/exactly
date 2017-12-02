import unittest

from exactly_lib_test.util.textformat import formatting, structure, parse, utils, construction


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        formatting.suite(),
        structure.suite(),
        parse.suite(),
        utils.suite(),
        construction.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
