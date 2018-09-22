import unittest

from exactly_lib_test.help.entities.concepts import all_concepts, render


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        render.suite(),
        all_concepts.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
