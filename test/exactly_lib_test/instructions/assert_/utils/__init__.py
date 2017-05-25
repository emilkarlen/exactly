import unittest

from exactly_lib_test.instructions.assert_.utils import instruction_from_parts_that_executes_sub_process, \
    instruction_from_parts


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        instruction_from_parts.suite(),
        instruction_from_parts_that_executes_sub_process.suite(),
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
