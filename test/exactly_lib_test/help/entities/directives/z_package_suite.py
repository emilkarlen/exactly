import unittest

from exactly_lib_test.help.entities.directives import object_documentations, render


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        render.suite(),
        object_documentations.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
