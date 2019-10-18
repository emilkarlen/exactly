from exactly_lib.common import result_reporting as reporting
from exactly_lib.common.err_msg.msg import minors, domain_objects, majors
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.report_rendering.parts import source_location
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.processing import exit_values
from exactly_lib.section_document import exceptions as sec_doc_exceptions
from exactly_lib.test_suite.file_reading import exception as suite_exception
from exactly_lib.test_suite.file_reading.exception import SuiteParseError, SuiteReadError, SuiteReadErrorVisitor
from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.render import combinators as comb
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering import line_elements
from exactly_lib.util.simple_textstruct.structure import MajorBlock

_SUITE_FILE_INCLUSION_CYCLE = 'The suite has already been included.'


def report_suite_parse_error(ex: SuiteParseError,
                             stdout_printer: FilePrinter,
                             stderr_printer: FilePrinter,
                             ) -> int:
    exit_value = _GetParseErrorExitValue().visit(ex.document_parser_exception)
    stdout_printer.write_colored_line(exit_value.exit_identifier, exit_value.color)
    stdout_printer.file.flush()

    blocks_renderer = _suite_parse_error_renderer(ex)
    reporting.print_major_blocks(blocks_renderer,
                                 stderr_printer)

    return exit_value.exit_code


def print_suite_read_error(ex: SuiteReadError, printer: FilePrinter):
    blocks_renderer = _suite_read_error_renderer(ex)

    reporting.print_major_blocks(blocks_renderer, printer)


def _suite_parse_error_renderer(ex: SuiteParseError) -> SequenceRenderer[MajorBlock]:
    blocks_renderers = [
        source_location.location_blocks_renderer(ex.source_location,
                                                 ex.maybe_section_name,
                                                 None),
        _error_message_blocks__parse_error(ex),
    ]
    return comb.ConcatenationR(blocks_renderers)


def _suite_read_error_renderer(ex: SuiteReadError) -> SequenceRenderer[MajorBlock]:
    blocks_renderers = [
        source_location.location_blocks_renderer(ex.source_location,
                                                 ex.maybe_section_name,
                                                 None),
        _error_message_blocks__read_error(ex),
    ]
    return comb.ConcatenationR(blocks_renderers)


def _error_message_blocks__parse_error(ex: SuiteParseError) -> SequenceRenderer[MajorBlock]:
    return _GetParseErrorErrorMessageLinesRenderer().visit(ex.document_parser_exception)


def _error_message_blocks__read_error(ex: SuiteReadError) -> SequenceRenderer[MajorBlock]:
    return _GetReadErrorMessageLinesRenderer().visit(ex)


class _GetParseErrorExitValue(sec_doc_exceptions.ParseErrorVisitor[ExitValue]):
    def visit_file_source_error(self, ex: sec_doc_exceptions.FileSourceError) -> ExitValue:
        return exit_values.NO_EXECUTION__SYNTAX_ERROR

    def visit_file_access_error(self, ex: sec_doc_exceptions.FileAccessError) -> ExitValue:
        return exit_values.NO_EXECUTION__FILE_ACCESS_ERROR


class _GetParseErrorErrorMessageLinesRenderer(sec_doc_exceptions.ParseErrorVisitor[TextRenderer]):
    def visit_file_source_error(self, ex: sec_doc_exceptions.FileSourceError) -> TextRenderer:
        return majors.of_minor(
            minors.syntax_error_message(line_elements.single_pre_formatted(ex.message))
        )

    def visit_file_access_error(self, ex: sec_doc_exceptions.FileAccessError) -> TextRenderer:
        return majors.of_minor(
            minors.file_access_error_message(line_elements.single_pre_formatted(ex.message))
        )


class _GetReadErrorMessageLinesRenderer(SuiteReadErrorVisitor[TextRenderer]):
    def visit_parse_error(self, ex: suite_exception.SuiteParseError) -> TextRenderer:
        return _GetParseErrorErrorMessageLinesRenderer().visit(ex.document_parser_exception)

    def visit_double_inclusion_error(self, ex: suite_exception.SuiteDoubleInclusion) -> TextRenderer:
        return majors.of_pre_formatted_message(_SUITE_FILE_INCLUSION_CYCLE)

    def visit_file_reference_error(self, ex: suite_exception.SuiteFileReferenceError) -> TextRenderer:
        return majors.of_minor(
            minors.header_and_message(
                ex.error_message_header,
                domain_objects.single_path(ex.reference),
            )
        )
