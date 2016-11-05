from exactly_lib.cli.cli_environment.program_modes.test_case import exit_values
from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case import phase_identifier
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.main_program import main_program_check_for_test_case
from exactly_lib_test.test_resources.process import ExpectedSubProcessResult
from exactly_lib_test.test_resources.value_assertions import process_result_info_assertions

IF_BASENAME_IS_PASS_THEN_EMPTY_TC_ELSE_TC_THAT_WILL_CAUSE_PARSER_ERROR = """
import sys
import os.path
import os

basename = os.path.basename(sys.argv[1])
if basename == 'pass':
    print('{section_header_for_phase_with_instructions}' + os.linesep + '# valid empty test case that PASS')
else:
    print('{section_header_for_phase_with_instructions}' + os.linesep + 'invalid test case that will cause PARSER-ERROR')
""".format(section_header_for_phase_with_instructions=section_header(phase_identifier.SETUP.section_name))


class TransformationIntoTestCaseThatPass(main_program_check_for_test_case.SetupWithPreprocessorAndTestActor):
    def file_argument_base_name(self) -> str:
        return 'pass'

    def test_case(self) -> str:
        return lines_content([
            section_header(phase_identifier.SETUP.section_name),
            'invalid test case that will would PARSE-ERROR, if it was not preprocessed'
        ])

    def preprocessor_source(self) -> str:
        return IF_BASENAME_IS_PASS_THEN_EMPTY_TC_ELSE_TC_THAT_WILL_CAUSE_PARSER_ERROR

    def expected_result(self) -> ExpectedSubProcessResult:
        return process_result_info_assertions.process_result_for_exit_value(exit_values.EXECUTION__PASS)


class TransformationIntoTestCaseThatParserError(main_program_check_for_test_case.SetupWithPreprocessorAndTestActor):
    def file_argument_base_name(self) -> str:
        return 'invalid'

    def test_case(self) -> str:
        return lines_content([
            section_header(phase_identifier.SETUP.section_name),
            '# valid empty test case that would PASS, if it was not preprocessed'
        ])

    def preprocessor_source(self) -> str:
        return IF_BASENAME_IS_PASS_THEN_EMPTY_TC_ELSE_TC_THAT_WILL_CAUSE_PARSER_ERROR

    def expected_result(self) -> ExpectedSubProcessResult:
        return process_result_info_assertions.is_process_result_for_exit_code(exit_values.NO_EXECUTION_EXIT_CODE)
