import unittest

from exactly_lib_test.instructions.assert_.utils.file_contents.parts import file_assertion_part


def suite() -> unittest.TestSuite:
    return file_assertion_part.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
