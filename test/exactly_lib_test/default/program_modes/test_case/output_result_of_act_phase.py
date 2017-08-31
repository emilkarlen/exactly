import unittest

from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import \
    OPTION_FOR_EXECUTING_ACT_PHASE
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, process_result_info_assertions


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    tests = [
        OutputAndExitCodeFromActPhaseIsEmittedAsResultWhenOptionForExecutingActPhaseIsGiven(),
    ]
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_without_preprocessor(tests, main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


class OutputAndExitCodeFromActPhaseIsEmittedAsResultWhenOptionForExecutingActPhaseIsGiven(
    SetupWithoutPreprocessorAndTestActor):
    def additional_arguments(self) -> list:
        return [OPTION_FOR_EXECUTING_ACT_PHASE]

    def test_case(self) -> str:
        test_case_source = """
[act]
import os
import sys
sys.stdout.write("output to stdout")
sys.stderr.write("output to stderr\\n")
sys.exit(72)
"""
        return test_case_source

    def expected_result(self) -> asrt.ValueAssertion:
        exit_code = 72
        std_out = 'output to stdout'
        std_err = 'output to stderr\n'
        return process_result_info_assertions.assertion_on_process_result(
            asrt.And([
                asrt.sub_component('exit code',
                                   SubProcessResult.exitcode.fget,
                                   asrt.Equals(exit_code)),
                asrt.sub_component('stdout',
                                   SubProcessResult.stdout.fget,
                                   asrt.Equals(std_out)),
                asrt.sub_component('stderr',
                                   SubProcessResult.stderr.fget,
                                   asrt.Equals(std_err)),
            ])
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
