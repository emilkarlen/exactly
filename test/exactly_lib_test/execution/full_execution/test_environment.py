import unittest

from exactly_lib_test.execution.full_execution.environment_tests_impl import \
    test_environment_variables, \
    test_current_directory


class Test(unittest.TestCase):
    def test_current_directory_for_each_phase_step(self):
        test_current_directory.Test(self).execute()

    def test_environment_variables_for_each_phase_step(self):
        test_environment_variables.Test(self).execute()
