from shellcheck_lib.cli.execution_mode.test_case.execution import NO_EXECUTION_EXIT_CODE
from shellcheck_lib_test.util.main_program import main_program_check_for_test_case
from shellcheck_lib_test.util.with_tmp_file import ExpectedSubProcessResult

IF_BASENAME_IS_PASS_THEN_EMPTY_TC_ELSE_TC_THAT_WILL_CAUSE_PARSER_ERROR = """
import sys
import os.path

basename = os.path.basename(sys.argv[1])
if basename == 'pass':
    print('# valid empty test case that PASS')
else:
    print('invalid test case that will cause PARSER-ERROR')
"""


class TransformationIntoTestCaseThatPass(main_program_check_for_test_case.SetupWithPreprocessor):
    def file_argument_base_name(self) -> str:
        return 'pass'

    def test_case(self) -> str:
        return """
invalid test case that will would PARSE-ERROR, if it was not preprocessed
"""

    def preprocessor_source(self) -> str:
        return IF_BASENAME_IS_PASS_THEN_EMPTY_TC_ELSE_TC_THAT_WILL_CAUSE_PARSER_ERROR

    def expected_result(self) -> ExpectedSubProcessResult:
        return ExpectedSubProcessResult(exitcode=0)


class TransformationIntoTestCaseThatParserError(main_program_check_for_test_case.SetupWithPreprocessor):
    def file_argument_base_name(self) -> str:
        return 'invalid'

    def test_case(self) -> str:
        return """
# valid empty test case that would PASS, if it was not preprocessed
"""

    def preprocessor_source(self) -> str:
        return IF_BASENAME_IS_PASS_THEN_EMPTY_TC_ELSE_TC_THAT_WILL_CAUSE_PARSER_ERROR

    def expected_result(self) -> ExpectedSubProcessResult:
        return ExpectedSubProcessResult(exitcode=NO_EXECUTION_EXIT_CODE)
