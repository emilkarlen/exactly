import unittest

from exactly_lib_test.help.syntax_elements import syntax_element_documentations, render


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        render.suite(),
        syntax_element_documentations.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
