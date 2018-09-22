import unittest

from exactly_lib_test.execution.impl import phase_step_execution, single_instruction_executor
from exactly_lib_test.execution.impl.phase_step_executors import z_package_suite as phase_step_executors
from exactly_lib_test.execution.impl.symbols_handling import z_package_suite as symbols_handling


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        symbols_handling.suite(),
        single_instruction_executor.suite(),
        phase_step_execution.suite(),
        phase_step_executors.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
