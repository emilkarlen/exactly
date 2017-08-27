import unittest

from exactly_lib_test.instructions.assert_.utils import instruction_from_parts_that_executes_sub_process, \
    instruction_from_parts, return_pfh_via_exceptions, \
    expression, checker


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        return_pfh_via_exceptions.suite(),
        instruction_from_parts.suite(),
        instruction_from_parts_that_executes_sub_process.suite(),
        checker.suite(),
        expression.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
