import unittest

from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds_files
from exactly_lib.util.string import lines_content
from exactly_lib_test.execution.partial_execution.test_resources import result_assertions as asrt_partial_result
from exactly_lib_test.execution.partial_execution.test_resources.act_phase_handling import \
    act_phase_handling_for_execution_of_python_source
from exactly_lib_test.execution.partial_execution.test_resources.basic import test__va, Arrangement, result_assertion
from exactly_lib_test.execution.test_resources import result_assertions as asrt_atc
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_assertions import \
    sds_root_dir_exists_and_has_sds_dirs
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    result_dir_contains_exactly
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources import py_program


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Case:
    def __init__(self,
                 name: str,
                 python_src: str,
                 expectation: SubProcessResult
                 ):
        self.name = name
        self.python_src = python_src
        self.expectation = expectation


class Test(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        cases = [
            Case('zero exit code, no output',
                 lines_content(py_program.exit_with_code(0)),
                 SubProcessResult(exitcode=0,
                                  stdout='',
                                  stderr=''),
                 ),
        ]
        empty_test_case = partial_test_case_with_instructions()
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                test__va(
                    self,
                    empty_test_case,
                    Arrangement(act_phase_handling=act_phase_handling_for_execution_of_python_source(case.python_src)),
                    result_assertion(partial_result=is_pass_with(case.expectation)),
                    is_keep_sandbox_during_assertions=True)


py_pgm = lines_content(py_program.exit_with_code(0))


def is_pass_with(expectation: SubProcessResult) -> asrt.ValueAssertion[PartialExeResult]:
    return asrt_partial_result.is_pass(
        action_to_check_outcome=asrt_atc.is_exit_code(expectation.exitcode),
        sds=asrt.and_([
            sds_root_dir_exists_and_has_sds_dirs(),
            result_dir_contains_exactly(result_files(expectation))
        ]))


def result_files(expectation: SubProcessResult) -> DirContents:
    return DirContents([
        File(sds_files.RESULT_FILE__EXITCODE, str(expectation.exitcode)),
        File(sds_files.RESULT_FILE__STDOUT, expectation.stdout),
        File(sds_files.RESULT_FILE__STDERR, expectation.stderr),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
