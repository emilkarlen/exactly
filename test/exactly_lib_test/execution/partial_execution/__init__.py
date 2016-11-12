import unittest

from exactly_lib_test.execution.partial_execution import \
    act_phase_execution, \
    instruction_environment, \
    deletion_of_sds, \
    phase_step_sequence, \
    environment_variables


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(act_phase_execution.suite())
    ret_val.addTest(instruction_environment.suite())
    ret_val.addTest(deletion_of_sds.suite())
    ret_val.addTest(phase_step_sequence.suite())
    ret_val.addTest(environment_variables.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
