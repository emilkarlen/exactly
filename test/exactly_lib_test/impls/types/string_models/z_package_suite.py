import unittest

from exactly_lib_test.impls.types.string_models import model_from_lines_base, model_of_file


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        model_from_lines_base.suite(),
        model_of_file.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
