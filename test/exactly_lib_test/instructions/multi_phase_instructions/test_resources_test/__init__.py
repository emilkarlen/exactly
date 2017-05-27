import unittest

from exactly_lib_test.instructions.multi_phase_instructions.test_resources_test import \
    instruction_embryo_check_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        instruction_embryo_check_test.suite(),
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
