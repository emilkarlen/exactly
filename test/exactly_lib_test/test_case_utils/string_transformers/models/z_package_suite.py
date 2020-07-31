import unittest

from exactly_lib_test.test_case_utils.string_transformers.models import transformed_by_program, from_writer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        transformed_by_program.suite(),
        from_writer.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
