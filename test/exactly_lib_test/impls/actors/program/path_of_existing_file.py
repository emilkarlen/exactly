import unittest

from exactly_lib.impls.actors.program import actor as sut
from exactly_lib_test.execution.test_resources import eh_assertions as asrt_eh
from exactly_lib_test.impls.actors.test_resources import integration_check
from exactly_lib_test.impls.actors.test_resources import relativity_configurations
from exactly_lib_test.impls.actors.test_resources.integration_check import Arrangement, Expectation, PostSdsExpectation
from exactly_lib_test.impls.types.program.test_resources import arguments_building as args
from exactly_lib_test.impls.types.test_resources.validation import pre_sds_validation_fails__svh
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources import py_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestDefaultRelativityOfExistingPath(),
        TestValidationErrorWhenExecutableFileDoesNotExist(),
    ])


class TestDefaultRelativityOfExistingPath(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        result = SubProcessResult(
            exitcode=5,
            stdout='output on stdout from existing py program file',
            stderr='output on stderr from existing py program file',
        )

        py_file = fs.File(
            'the-program.py',
            py_program.program_that_prints_and_exits_with_exit_code(result),
        )

        source_w_relative_name_of_existing_file = args.interpret_py_source_file(py_file.name)

        # ACT & ASSERT #

        integration_check.check_execution(
            self,
            sut.actor(),
            [instr(source_w_relative_name_of_existing_file.as_arguments.lines)],
            Arrangement(
                hds_contents=relativity_configurations.PROGRAM_FILE.populator_for_relativity_option_root__hds(
                    DirContents([py_file]))
            ),
            Expectation(
                execute=asrt_eh.is_exit_code(result.exitcode),
                post_sds=PostSdsExpectation.constant(
                    sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                        exit_code=asrt.equals(result.exitcode),
                        stdout=asrt.equals(result.stdout),
                        stderr=asrt.equals(result.stderr),
                    )
                )
            ),
        )


class TestValidationErrorWhenExecutableFileDoesNotExist(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        source_w_relative_name_of_existing_file = args.interpret_py_source_file('program.py')

        # ACT & ASSERT #

        integration_check.check_execution(
            self,
            sut.actor(),
            [instr(source_w_relative_name_of_existing_file.as_arguments.lines)],
            Arrangement(),
            Expectation(
                validation=pre_sds_validation_fails__svh()
            ),
        )
