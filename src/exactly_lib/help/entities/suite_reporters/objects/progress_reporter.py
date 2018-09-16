from exactly_lib.common.exit_value import ExitValue
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.doc_format import exit_value_text
from exactly_lib.definitions.entity.suite_reporters import PROGRESS_REPORTER
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.help.entities.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.processing import exit_values as case_exit_values
from exactly_lib.test_suite import exit_values
from exactly_lib.test_suite.reporters import simple_progress_reporter as reporter
from exactly_lib.util.textformat.structure.structures import *
from exactly_lib.util.textformat.textformat_parser import TextParser


class SimpleProgressSuiteReporterDocumentation(SuiteReporterDocumentation):
    def __init__(self):
        super().__init__(PROGRESS_REPORTER)
        format_map = {
        }
        self._parser = TextParser(format_map)

    def syntax_of_output(self) -> List[ParagraphItem]:
        return self._parser.fnap(_SYNTAX_OF_OUTPUT)

    def exit_code_description(self) -> List[ParagraphItem]:
        return (self._parser.fnap(_EXIT_CODE_DESCRIPTION_PRELUDE) +
                [self._exit_value_table(_exit_values_and_descriptions())])

    def _exit_value_table(self, exit_value_and_description_list: list) -> ParagraphItem:
        def _row(exit_value: ExitValue, description: str) -> List[TableCell]:
            return [
                cell(paras(str(exit_value.exit_code))),
                cell(paras(exit_value_text(exit_value))),
                cell(self._parser.fnap(description)),
            ]

        return first_row_is_header_table(
            [
                [
                    cell(paras(misc_texts.EXIT_CODE_TITLE)),
                    cell(paras(misc_texts.EXIT_IDENTIFIER_TITLE)),
                    cell(paras('When')),
                ]] +
            [_row(exit_value, description) for exit_value, description in exit_value_and_description_list],
            '  ')


DOCUMENTATION = SimpleProgressSuiteReporterDocumentation()

_SYNTAX_OF_OUTPUT = """\
Reports one event per line:


 * beginning of test suite
 * execution of test case
 * end of test suite


Beginning and end of test suites wraps the test cases that are contained directly in the test suite
(i.e. it does not wrap test cases that are contained in sub suites).


Last line is an exit identifier, that depends on the outcome of the suite, and is related to the exit code.

A summary is printed on stderr.
"""

_EXIT_CODE_DESCRIPTION_PRELUDE = """\
Exit codes, and corresponding exit identifiers printed as the last line of stdout:
"""


def _exit_values_list(full_result_statuses) -> str:
    evs = map(case_exit_values.from_full_result, full_result_statuses)
    return ', '.join(sorted(map(ExitValue.exit_identifier.fget, evs)))


def _all_pass_description() -> str:
    return ('All test cases could be executed, and result was one of ' +
            _exit_values_list(reporter.SUCCESS_STATUSES) +
            '.')


def _failed_tests_description() -> str:
    non_pass_result_statuses = set()
    for st in list(FullExeResultStatus):
        if st not in reporter.SUCCESS_STATUSES:
            non_pass_result_statuses.add(st)
    return ("""\
At least one test case could not be executed,
or was executed with a result other than those above:
""" + _exit_values_list(non_pass_result_statuses) +
            '.'
            )


_INVALID_SUITE_DESCRIPTION = """\
There was an error reading the test suite.

No test cases have been executed.
"""


def _exit_values_and_descriptions() -> list:
    return [
        (exit_values.ALL_PASS, _all_pass_description()),
        (exit_values.FAILED_TESTS, _failed_tests_description()),
        (exit_values.INVALID_SUITE, _INVALID_SUITE_DESCRIPTION),
    ]
