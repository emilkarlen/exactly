from exactly_lib.help.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help.suite_reporters.names_and_cross_references import JUNIT_REPORTER__NAME
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs


class JunitSuiteReporterDocumentation(SuiteReporterDocumentation):
    def __init__(self):
        super().__init__(JUNIT_REPORTER__NAME)
        format_map = {
        }
        self._parser = TextParser(format_map)

    def single_line_description_str(self) -> str:
        return self._parser.format('Outputs JUnit XML.')

    def syntax_of_output(self) -> list:
        return normalize_and_parse(_SYNTAX_OF_OUTPUT)

    def exit_code_description(self) -> list:
        return docs.paras('Unconditionally 0.')


_SYNTAX_OF_OUTPUT = """\
https://windyroad.com.au/dl/Open Source/JUnit.xsd


as of 2016-11-14.
"""
