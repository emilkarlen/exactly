import unittest

from exactly_lib_test.help.entities.types import render, all_types


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        render.suite(),
        all_types.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
