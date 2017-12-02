import unittest

from exactly_lib_test.util.textformat import rendering, structure, parse, utils, construction


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        rendering.suite(),
        structure.suite(),
        parse.suite(),
        utils.suite(),
        construction.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
