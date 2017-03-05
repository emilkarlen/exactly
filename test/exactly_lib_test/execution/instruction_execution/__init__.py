import unittest

from exactly_lib_test.execution.instruction_execution import phase_step_execution, \
    single_instruction_executor, value_definition_validation, phase_step_executors


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(single_instruction_executor.suite())
    ret_val.addTest(phase_step_execution.suite())
    ret_val.addTest(value_definition_validation.suite())
    ret_val.addTest(phase_step_executors.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
