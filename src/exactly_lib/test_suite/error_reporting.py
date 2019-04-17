from typing import List

from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.result_reporting import output_location
from exactly_lib.processing import exit_values
from exactly_lib.section_document import exceptions as sec_doc_exceptions
from exactly_lib.test_case import error_description
from exactly_lib.test_suite.file_reading import exception as suite_exception
from exactly_lib.test_suite.file_reading.exception import SuiteParseError, SuiteReadError, SuiteReadErrorVisitor
from exactly_lib.util.std import FilePrinter


def report_suite_parse_error(ex: SuiteParseError,
                             stdout_printer: FilePrinter,
                             stderr_printer: FilePrinter,
                             ) -> int:
    exit_value = _GetParseErrorExitValue().visit(ex.document_parser_exception)
    stdout_printer.write_colored_line(exit_value.exit_identifier, exit_value.color)
    stdout_printer.file.flush()
    output_location(stderr_printer,
                    ex.source_location,
                    ex.maybe_section_name,
                    None)
    stderr_printer.write_lines(error_message_lines__parse_error(ex))
    return exit_value.exit_code


def error_message_lines__parse_error(ex: SuiteParseError) -> List[str]:
    return _ParseErrorErrorMessageLinesRenderer().visit(ex.document_parser_exception)


def error_message_lines(ex: SuiteReadError) -> List[str]:
    return _ErrorMessageLinesRenderer().visit(ex)


class _GetParseErrorExitValue(sec_doc_exceptions.ParseErrorVisitor[ExitValue]):
    def visit_file_source_error(self, ex: sec_doc_exceptions.FileSourceError) -> ExitValue:
        return exit_values.NO_EXECUTION__SYNTAX_ERROR

    def visit_file_access_error(self, ex: sec_doc_exceptions.FileAccessError) -> ExitValue:
        return exit_values.NO_EXECUTION__FILE_ACCESS_ERROR


class _ParseErrorErrorMessageLinesRenderer(sec_doc_exceptions.ParseErrorVisitor[List[str]]):
    def visit_file_source_error(self, ex: sec_doc_exceptions.FileSourceError) -> List[str]:
        return [error_description.syntax_error_message(ex.message)]

    def visit_file_access_error(self, ex: sec_doc_exceptions.FileAccessError) -> List[str]:
        return [error_description.file_access_error_message(ex.message)]


class _ErrorMessageLinesRenderer(SuiteReadErrorVisitor[List[str]]):
    def visit_parse_error(self, ex: suite_exception.SuiteParseError) -> List[str]:
        return error_message_lines__parse_error(ex)

    def visit_double_inclusion_error(self, ex: suite_exception.SuiteDoubleInclusion) -> List[str]:
        return ['The suite has already been included.']

    def visit_file_reference_error(self, ex: suite_exception.SuiteFileReferenceError) -> List[str]:
        return [
            ex.error_message_header + ':',
            str(ex.reference)
        ]
