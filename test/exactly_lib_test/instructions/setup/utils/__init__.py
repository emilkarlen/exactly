import unittest

from exactly_lib_test.instructions.setup.utils import instruction_utils, \
    instruction_from_parts_that_executes_sub_process


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        instruction_utils.suite(),
        instruction_from_parts_that_executes_sub_process.suite(),
    ])


def run_suite():
    unittest.TextTestRunner().run(suite())


if __name__ == '__main__':
    run_suite()
