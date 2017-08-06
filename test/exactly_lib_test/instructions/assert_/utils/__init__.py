import unittest

from exactly_lib_test.instructions.assert_.utils import instruction_from_parts_that_executes_sub_process, \
    instruction_from_parts
from exactly_lib_test.instructions.assert_.utils.file_contents import env_vars_replacement


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        instruction_from_parts.suite(),
        instruction_from_parts_that_executes_sub_process.suite(),
        env_vars_replacement.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
