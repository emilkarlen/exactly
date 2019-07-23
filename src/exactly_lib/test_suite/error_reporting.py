from typing import Sequence

from exactly_lib.common import result_reporting as reporting
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import misc_texts
from exactly_lib.processing import exit_values
from exactly_lib.section_document import exceptions as sec_doc_exceptions
from exactly_lib.test_suite.file_reading import exception as suite_exception
from exactly_lib.test_suite.file_reading.exception import SuiteParseError, SuiteReadError, SuiteReadErrorVisitor
from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.name import Name
from exactly_lib.util.simple_textstruct import structure as struct
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as comb
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, minor_block_from_lines, StringLineObject, \
    PreFormattedStringLineObject, MinorBlock


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


def _suite_parse_error_renderer(ex: SuiteParseError) -> Renderer[Sequence[MajorBlock]]:
    blocks_renderers = [
        reporting.location_blocks_renderer(ex.source_location,
                                           ex.maybe_section_name,
                                           None),
        _error_message_blocks__parse_error(ex),
    ]
    return comb.ConcatenationR(blocks_renderers)


def _suite_read_error_renderer(ex: SuiteReadError) -> Renderer[Sequence[MajorBlock]]:
    blocks_renderers = [
        reporting.location_blocks_renderer(ex.source_location,
                                           ex.maybe_section_name,
                                           None),
        _error_message_blocks__read_error(ex),
    ]
    return comb.ConcatenationR(blocks_renderers)


def _error_message_blocks__parse_error(ex: SuiteParseError) -> Renderer[Sequence[MajorBlock]]:
    return _GetParseErrorErrorMessageLinesRenderer().visit(ex.document_parser_exception)


def _error_message_blocks__read_error(ex: SuiteReadError) -> Renderer[Sequence[MajorBlock]]:
    return _GetReadErrorMessageLinesRenderer().visit(ex)


class _GetParseErrorExitValue(sec_doc_exceptions.ParseErrorVisitor[ExitValue]):
    def visit_file_source_error(self, ex: sec_doc_exceptions.FileSourceError) -> ExitValue:
        return exit_values.NO_EXECUTION__SYNTAX_ERROR

    def visit_file_access_error(self, ex: sec_doc_exceptions.FileAccessError) -> ExitValue:
        return exit_values.NO_EXECUTION__FILE_ACCESS_ERROR


class _GetParseErrorErrorMessageLinesRenderer(sec_doc_exceptions.ParseErrorVisitor[TextRenderer]):
    def visit_file_source_error(self, ex: sec_doc_exceptions.FileSourceError) -> TextRenderer:
        return text_docs.text_renderer_of_constant_minor_block(
            _syntax_error_message(ex.message)
        )

    def visit_file_access_error(self, ex: sec_doc_exceptions.FileAccessError) -> TextRenderer:
        return text_docs.text_renderer_of_constant_minor_block(
            _file_access_error_message(ex.message)
        )


class _GetReadErrorMessageLinesRenderer(SuiteReadErrorVisitor[TextRenderer]):
    def visit_parse_error(self, ex: suite_exception.SuiteParseError) -> TextRenderer:
        return _GetParseErrorErrorMessageLinesRenderer().visit(ex.document_parser_exception)

    def visit_double_inclusion_error(self, ex: suite_exception.SuiteDoubleInclusion) -> TextRenderer:
        return text_docs.text_renderer_of_constant_minor_block(
            minor_block_from_lines([
                StringLineObject('The suite has already been included.'),
            ])
        )

    def visit_file_reference_error(self, ex: suite_exception.SuiteFileReferenceError) -> TextRenderer:
        return text_docs.text_renderer_of_constant_minor_block(
            minor_block_from_lines([
                StringLineObject(ex.error_message_header + ':'),
                PreFormattedStringLineObject(str(ex.reference), False),
            ])
        )


def _formatted_error_message_str(category: Name, message: str) -> MinorBlock:
    return MinorBlock(
        [
            struct.LineElement(struct.StringLineObject(category.singular.capitalize() + ': ')),
            struct.LineElement(struct.PreFormattedStringLineObject(message, False)),
        ]
    )


def _syntax_error_message(message: str) -> MinorBlock:
    return _formatted_error_message_str(misc_texts.SYNTAX_ERROR_NAME, message)


def _file_access_error_message(message: str) -> MinorBlock:
    return _formatted_error_message_str(misc_texts.FILE_ACCESS_ERROR_NAME,
                                        message)
