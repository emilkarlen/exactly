from exactly_lib.help.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help.suite_reporters.names_and_cross_references import JUNIT_REPORTER__NAME
from exactly_lib.help.utils.textformat_parser import TextParser


class JunitSuiteReporterDocumentation(SuiteReporterDocumentation):
    def __init__(self):
        super().__init__(JUNIT_REPORTER__NAME)
        format_map = {
        }
        self._parser = TextParser(format_map)

    def single_line_description_str(self) -> str:
        return self._parser.format('Prints JUnit xml.')
