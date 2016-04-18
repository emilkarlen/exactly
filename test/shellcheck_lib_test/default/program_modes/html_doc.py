import unittest

from shellcheck_lib.cli import main_program
from shellcheck_lib.cli.program_modes.help import arguments_for
from shellcheck_lib.default.program_modes.test_case import default_instructions_setup
from shellcheck_lib.help.contents_structure import application_help_for
from shellcheck_lib.help.html_doc import main as sut
from shellcheck_lib.util.textformat.formatting.html.document import DOCTYPE_XHTML1_0
from shellcheck_lib_test.test_resources import process_result_assertions as pr
from shellcheck_lib_test.test_resources import value_assertion as va
from shellcheck_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase, PlainArrangement
from shellcheck_lib_test.test_resources.main_program.constant_arguments_check_execution import test_suite_for_test_cases
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.str_std_out_files import null_output_files
from shellcheck_lib_test.test_resources.value_assertion_str import begins_with


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestHtmlDoc))
    ret_val.addTest(suite_for_main_program(main_program_runner))
    return ret_val


def suite_for_main_program(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return test_suite_for_test_cases(main_program_test_cases(), main_program_runner)


def main_program_test_cases() -> list:
    return [
        ProcessTestCase('Generation of html-doc SHOULD exit with 0 exitcode '
                        'AND output html',
                        PlainArrangement([main_program.HELP_COMMAND] + arguments_for.html_doc()),
                        va.And([
                            pr.is_result_for_exit_code(0),
                            pr.stdout(begins_with(DOCTYPE_XHTML1_0))
                        ])
                        )
    ]


class TestHtmlDoc(unittest.TestCase):
    def test_that_html_doc_generation_does_not_raise_an_exception(self):
        # ARRANGE #
        output = null_output_files()
        application_help = application_help_for(default_instructions_setup.INSTRUCTIONS_SETUP)
        generator = sut.HtmlDocGenerator(output, application_help)
        # ACT & ASSERT #
        generator.apply()
