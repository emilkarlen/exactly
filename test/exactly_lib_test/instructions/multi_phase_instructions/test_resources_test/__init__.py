import unittest

from exactly_lib_test.instructions.multi_phase_instructions.test_resources_test import \
    instruction_embryo_check_test


def suite() -> unittest.TestSuite:
    return instruction_embryo_check_test.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
