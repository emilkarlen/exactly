import pathlib
import unittest

from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import \
    OPTION_FOR_KEEPING_SANDBOX_DIRECTORY
from exactly_lib.processing import exit_values
from exactly_lib_test.default.program_modes.test_case.test_resources.utils import remove_if_is_directory, \
    get_printed_sds_or_fail
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_case_file_structure.sandbox_directory_structure import \
    is_sandbox_directory_structure_after_execution
from exactly_lib_test.test_resources.assertions.file_checks import FileChecker
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, process_result_info_assertions


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_without_preprocessor(SPECIAL_EXECUTION_CONFIGURATIONS_TESTS, main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


class FlagForPrintingAndPreservingSandbox(SetupWithoutPreprocessorAndTestActor):
    def test_case(self) -> str:
        return ''

    def additional_arguments(self) -> list:
        return [OPTION_FOR_KEEPING_SANDBOX_DIRECTORY]

    def expected_result(self) -> asrt.ValueAssertion:
        return process_result_info_assertions.assertion_on_process_result(
            asrt.And([
                asrt.sub_component('exit code',
                                   SubProcessResult.exitcode.fget,
                                   asrt.Equals(exit_values.EXECUTION__PASS.exit_code)),
                AssertStdoutIsNameOfExistingSandboxDirectory(),
            ]))


class AssertStdoutIsNameOfExistingSandboxDirectory(asrt.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value: SubProcessResult,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        actual_sds_directory = get_printed_sds_or_fail(put, value)
        actual_sds_path = pathlib.Path(actual_sds_directory)
        if actual_sds_path.exists():
            if actual_sds_path.is_dir():
                is_sandbox_directory_structure_after_execution(
                    FileChecker(put, 'Not an sandbox directory structure'),
                    actual_sds_directory)
                remove_if_is_directory(actual_sds_directory)
            else:
                put.fail('Output from program is not the sandbox (not a directory): "%s"' % actual_sds_directory)
        else:
            put.fail('The output from the program is not the sandbox: "%s"' % actual_sds_directory)


SPECIAL_EXECUTION_CONFIGURATIONS_TESTS = [
    FlagForPrintingAndPreservingSandbox(),
]

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
