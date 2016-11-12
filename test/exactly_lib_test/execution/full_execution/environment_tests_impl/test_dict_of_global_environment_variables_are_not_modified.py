import os
import unittest

from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib_test.execution.full_execution.test_resources.test_case_base import FullExecutionTestCaseBase
from exactly_lib_test.execution.partial_execution.test_resources.basic import dummy_act_phase_handling
from exactly_lib_test.execution.test_resources import recorder as instr_setup
from exactly_lib_test.execution.test_resources.test_case_generation import full_test_case_with_instructions


class Test(FullExecutionTestCaseBase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case,
                         dbg_do_not_delete_dir_structure)
        self.recorder = instr_setup.Recorder()
        self.original_set_of_env_vars = dict(os.environ)

    def _act_phase_handling(self) -> ActPhaseHandling:
        return dummy_act_phase_handling()

    def _test_case(self) -> test_case_doc.TestCase:
        return full_test_case_with_instructions()

    def _assertions(self):
        self.utc.assertDictEqual(self.original_set_of_env_vars,
                                 dict(os.environ))
