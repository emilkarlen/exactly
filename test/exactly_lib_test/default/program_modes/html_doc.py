import io
import unittest

from exactly_lib.cli.cli_environment.common_cli_options import HELP_COMMAND
from exactly_lib.cli.program_modes.help import arguments_for
from exactly_lib.default.program_modes.test_case import default_instructions_setup
from exactly_lib.help.contents_structure import application_help_for
from exactly_lib.help.html_doc import main as sut
from exactly_lib.util.textformat.formatting.html.document import DOCTYPE_XHTML1_0
from exactly_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase, PlainArrangement
from exactly_lib_test.test_resources.main_program.constant_arguments_check_execution import test_suite_for_test_cases
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion_str import begins_with


def complete_suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTests(suite_that_does_not_require_main_program_runner())
    ret_val.addTest(suite_that_does_require_main_program_runner(main_program_runner))
    return ret_val


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    return unittest.makeSuite(TestHtmlDoc)


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return test_suite_for_test_cases(_main_program_test_cases(), main_program_runner)


def _main_program_test_cases() -> list:
    return [
        ProcessTestCase('Generation of html-doc SHOULD exit with 0 exitcode '
                        'AND output html',
                        PlainArrangement([HELP_COMMAND] + arguments_for.html_doc()),
                        va.And([
                            pr.is_result_for_exit_code(0),
                            pr.stdout(begins_with(DOCTYPE_XHTML1_0))
                        ])
                        )
    ]


class TestHtmlDoc(unittest.TestCase):
    def test_generate_and_output_SHOULD_output_xhtml(self):
        # ARRANGE #
        application_help = application_help_for(default_instructions_setup.INSTRUCTIONS_SETUP)
        output_file = io.StringIO()
        # ACT #
        sut.generate_and_output(output_file, application_help)
        # ASSERT #
        actual_output = output_file.getvalue()
        begins_with(DOCTYPE_XHTML1_0).apply(self, actual_output, va.MessageBuilder('file output'))
