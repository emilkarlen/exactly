import unittest

from exactly_lib_test.impls.types.string_model.parse import contents_from_string, contents_from_file, \
    contents_from_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        contents_from_string.suite(),
        contents_from_file.suite(),
        contents_from_program.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
