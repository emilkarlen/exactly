import os
import unittest

from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib_test.execution.full_execution.test_resources.test_case_base import FullExecutionTestCaseBase
from exactly_lib_test.execution.test_resources import recorder as instr_setup
from exactly_lib_test.execution.test_resources.test_case_generation import full_test_case_with_instructions
from exactly_lib_test.test_case.actor.test_resources.actors import dummy_actor


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TheTest(),
    ])


class TheTest(unittest.TestCase):
    def runTest(self):
        TestExecutor(self).execute()


class TestExecutor(FullExecutionTestCaseBase):
    def __init__(self,
                 put: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False,
                 ):
        super().__init__(put,
                         dbg_do_not_delete_dir_structure)
        self.recorder = instr_setup.Recorder()
        self.original_set_of_env_vars = dict(os.environ)

    def _actor(self) -> Actor:
        return dummy_actor()

    def _test_case(self) -> test_case_doc.TestCase:
        return full_test_case_with_instructions()

    def _assertions(self):
        self.utc.assertDictEqual(self.original_set_of_env_vars,
                                 dict(os.environ))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
