import unittest

from exactly_lib_test.impls.types.string_model import model_from_lines_base, model_of_file
from exactly_lib_test.impls.types.string_model.parse import z_package_suite as parse


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        model_from_lines_base.suite(),
        model_of_file.suite(),
        parse.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
