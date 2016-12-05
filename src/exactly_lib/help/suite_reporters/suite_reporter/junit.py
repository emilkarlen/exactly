from exactly_lib.help.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help.suite_reporters.names_and_cross_references import JUNIT_REPORTER__NAME
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.test_suite.reporters.junit import UNCONDITIONAL_EXIT_CODE


class JunitSuiteReporterDocumentation(SuiteReporterDocumentation):
    def __init__(self):
        super().__init__(JUNIT_REPORTER__NAME)
        format_map = {
            'EXIT_CODE': str(UNCONDITIONAL_EXIT_CODE),
        }
        self._parser = TextParser(format_map)

    def single_line_description_str(self) -> str:
        return self._parser.format('Outputs JUnit XML.')

    def syntax_of_output(self) -> list:
        return self._parser.fnap(_SYNTAX_OF_OUTPUT)

    def exit_code_description(self) -> list:
        return self._parser.fnap(_EXIT_CODE_DESCRIPTION)


_SYNTAX_OF_OUTPUT = """\
https://windyroad.com.au/dl/Open Source/JUnit.xsd


as of 2016-11-14.


A suite without sub suites is reported as a
"""

_EXIT_CODE_DESCRIPTION = """\
Unconditionally {EXIT_CODE}.
"""
