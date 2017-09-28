import unittest

from exactly_lib_test.help.entities.syntax_elements import render
from exactly_lib_test.help.entities.syntax_elements import syntax_element_documentations


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        render.suite(),
        syntax_element_documentations.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
