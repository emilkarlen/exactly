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
        return self._parser.format(_SINGLE_LINE_DESCRIPTION)

    def exit_code_description(self) -> list:
        return self._parser.fnap(_EXIT_CODE_DESCRIPTION)


DOCUMENTATION = SimpleProgressSuiteReporterDocumentation()

_SINGLE_LINE_DESCRIPTION = 'Reports execution progress in a human readable form.'

_EXIT_CODE_DESCRIPTION = '0 iff all test cases passed.'
