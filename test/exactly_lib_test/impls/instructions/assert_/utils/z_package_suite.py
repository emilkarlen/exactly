import unittest

from exactly_lib_test.impls.instructions.assert_.utils import instruction_from_parts_that_executes_sub_process, \
    instruction_from_parts, return_pfh_via_exceptions, \
    assertion_part, file_contents
from exactly_lib_test.impls.instructions.assert_.utils.file_contents import z_package_suite as file_contents


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        return_pfh_via_exceptions.suite(),
        instruction_from_parts.suite(),
        instruction_from_parts_that_executes_sub_process.suite(),
        assertion_part.suite(),
        file_contents.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
