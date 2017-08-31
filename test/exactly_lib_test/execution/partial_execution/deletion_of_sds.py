import unittest

from exactly_lib.execution import partial_execution as sut
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.execution.partial_execution.test_resources.basic import test, dummy_act_phase_handling, \
    Result
from exactly_lib_test.execution.test_resources.instruction_test_resources import act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_keep_execution_directory_root(self):
        test(
            self,
            test_case_that_does_nothing(),
            dummy_act_phase_handling(),
            sandbox_directory_structure_exists,
            is_keep_sandbox=True)

    def test_do_not_keep_execution_directory_root(self):
        test(
            self,
            test_case_that_does_nothing(),
            dummy_act_phase_handling(),
            sandbox_directory_structure_does_not_exist,
            is_keep_sandbox=False)


def sandbox_directory_structure_exists(put: unittest.TestCase,
                                       actual: Result):
    _common_assertions(actual, put)
    put.assertTrue(actual.partial_result.sds.root_dir.is_dir())


def sandbox_directory_structure_does_not_exist(put: unittest.TestCase,
                                               actual: Result):
    _common_assertions(actual, put)
    put.assertFalse(actual.partial_result.sds.root_dir.exists())


def _common_assertions(actual, put):
    put.assertTrue(actual.partial_result.has_sds,
                   'SDS is expected to have been created')


def test_case_that_does_nothing() -> sut.TestCase:
    return partial_test_case_with_instructions(
        act_phase_instructions=[act_phase_instruction_with_source(LineSequence(1, ('line',)))],
    )


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
