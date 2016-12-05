from exactly_lib.help.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help.suite_reporters.names_and_cross_references import PROGRESS_REPORTER__NAME
from exactly_lib.help.utils.textformat_parser import TextParser


class SimpleProgressSuiteReporterDocumentation(SuiteReporterDocumentation):
    def __init__(self):
        super().__init__(PROGRESS_REPORTER__NAME)
        format_map = {
        }
        self._parser = TextParser(format_map)

    def single_line_description_str(self) -> str:
        return self._parser.format('Print a single line per test case.')

    def exit_code_description(self) -> list:
        return self._parser.fnap('0 if all test cases passed.')


DOCUMENTATION = SimpleProgressSuiteReporterDocumentation()
