from exactly_lib.help.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help.suite_reporters.names_and_cross_references import JUNIT_REPORTER
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.test_suite.reporters import junit


class JunitSuiteReporterDocumentation(SuiteReporterDocumentation):
    def __init__(self):
        super().__init__(JUNIT_REPORTER)
        format_map = {
            'EXIT_CODE': str(junit.UNCONDITIONAL_EXIT_CODE),
            'test_suite_element': junit.TEST_SUITE_ELEMENT_NAME,
            'test_suites_element': junit.TEST_SUITES_ELEMENT_NAME,
        }
        self._parser = TextParser(format_map)

    def syntax_of_output(self) -> list:
        return self._parser.fnap(_SYNTAX_OF_OUTPUT)

    def exit_code_description(self) -> list:
        return self._parser.fnap(_EXIT_CODE_DESCRIPTION)


_SYNTAX_OF_OUTPUT = """\
https://windyroad.com.au/dl/Open Source/JUnit.xsd

as of 2016-11-14.


A suite with sub suites is reported as a '{test_suites_element}' element.


A suite without sub suites is reported as a '{test_suite_element}' element.
"""

_EXIT_CODE_DESCRIPTION = """\
Unconditionally {EXIT_CODE}.
"""
