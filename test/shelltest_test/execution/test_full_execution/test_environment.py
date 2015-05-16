import unittest

from shelltest_test.execution.test_full_execution.test_case_impl import test_environment_variables


class Test(unittest.TestCase):
    def test_environment_variables_for_each_phase_step(self):
        test_environment_variables.Test(self).execute()
