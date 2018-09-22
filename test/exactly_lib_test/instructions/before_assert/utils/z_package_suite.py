import unittest

from exactly_lib_test.instructions.before_assert.utils import instruction_from_parts_that_executes_sub_process, \
    instruction_from_parts


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        instruction_from_parts.suite(),
        instruction_from_parts_that_executes_sub_process.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
