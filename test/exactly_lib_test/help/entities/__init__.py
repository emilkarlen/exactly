import unittest

from exactly_lib_test.help.entities import actors, suite_reporters, concepts, syntax_elements


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(concepts.suite())
    ret_val.addTest(actors.suite())
    ret_val.addTest(suite_reporters.suite())
    ret_val.addTest(syntax_elements.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
