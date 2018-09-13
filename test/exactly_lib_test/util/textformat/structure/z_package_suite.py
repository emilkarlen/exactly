import unittest

from exactly_lib_test.util.textformat.structure import core, document


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        core.suite(),
        document.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
