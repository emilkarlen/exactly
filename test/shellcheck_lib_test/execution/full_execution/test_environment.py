import unittest

from shellcheck_lib_test.execution.full_execution.test_case_impl import \
    test_environment_variables, \
    test_current_directory


class Test(unittest.TestCase):
    def test_environment_variables_for_each_phase_step(self):
        test_environment_variables.Test(self).execute()

    def test_current_directory_for_each_phase_step(self):
        test_current_directory.Test(self).execute()
