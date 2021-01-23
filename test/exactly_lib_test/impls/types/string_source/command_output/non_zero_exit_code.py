import unittest
from typing import List, Callable

from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.types.string_source.command_output.test_resources import ModelMaker, \
    SourceConstructorForPySourceProgramViaCmdLine
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.string_source.test_resources import contents_assertions as asrt_str_src_contents
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestNonZeroExitCode),
    ])


class TestNonZeroExitCode(unittest.TestCase):
    def test_result_SHOULD_be_failure_WHEN_non_zero_exit_code_and_exit_code_is_not_ignored(self):
        self._check_exit_codes(
            exit_code_cases=[1, 69],
            ignore_exit_code=False,
            expected_primitive=self._contents_access_raises_hard_error
        )

    def test_result_SHOULD_be_success_WHEN_any_zero_exit_code_and_exit_code_is_ignored(self):
        self._check_exit_codes(
            exit_code_cases=[0, 1, 2, 69],
            ignore_exit_code=True,
            expected_primitive=self._contents_is_output_from_program,
        )

    def _check_exit_codes(self,
                          exit_code_cases: List[int],
                          ignore_exit_code: bool,
                          expected_primitive: Callable[[str], multi_obj_assertions.ExpectationOnUnFrozenAndFrozen],
                          ):
        # ARRANGE #

        program_output = {
            ProcOutputFile.STDOUT: 'output on stdout',
            ProcOutputFile.STDERR: 'output on stderr',
        }

        for exit_code in exit_code_cases:
            py_program = py_programs.py_pgm_with_stdout_stderr_exit_code(
                exit_code=exit_code,
                stdout_output=program_output[ProcOutputFile.STDOUT],
                stderr_output=program_output[ProcOutputFile.STDERR],
            )
            for output_file in ProcOutputFile:
                expected_program_output = program_output[output_file]
                with self.subTest(exit_code=exit_code,
                                  output_file=output_file):
                    source_constructors = SourceConstructorForPySourceProgramViaCmdLine(
                        py_program,
                        ModelMaker(
                            ignore_exit_code=ignore_exit_code,
                            output_channel_to_capture=output_file,
                            mem_buff_size=1,
                        )
                    )
                    assertion = multi_obj_assertions.assertion_of_2_seq_w_file_first_and_last(
                        expected_primitive(expected_program_output),
                    )
                    # ACT & ASSERT #
                    assertion.apply_without_message(
                        self,
                        source_constructors.build(),
                    )

    @staticmethod
    def _contents_access_raises_hard_error(contents_on_output_channel: str,
                                           ) -> multi_obj_assertions.ExpectationOnUnFrozenAndFrozen:
        return multi_obj_assertions.ExpectationOnUnFrozenAndFrozen(
            asrt_str_src_contents.Expectation.hard_error(
                may_depend_on_external_resources=asrt_str_src_contents.external_dependencies__const(True),
            ),
            frozen_may_depend_on_external_resources=asrt_str_src_contents.ext_dependencies_raises_hard_error()
        )

    @staticmethod
    def _contents_is_output_from_program(contents_on_output_channel: str,
                                         ) -> multi_obj_assertions.ExpectationOnUnFrozenAndFrozen:
        return multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
            contents_on_output_channel,
            may_depend_on_external_resources=asrt.equals(True),
            frozen_may_depend_on_external_resources=asrt.equals(True),
        )
