import io

from exactly_lib.common.report_rendering import print
from exactly_lib.common.report_rendering.parts import full_exec_result
from exactly_lib.common.report_rendering.parts.error_info import ErrorInfoRenderer
from exactly_lib.execution.full_execution.result import FullExeResult
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering import component_renderers as rend
from exactly_lib.util.simple_textstruct.structure import MajorBlock


def error_message_for_full_result(the_full_result: FullExeResult) -> str:
    output_file = io.StringIO()
    print_error_message_for_full_result(FilePrinter(output_file), the_full_result)
    return output_file.getvalue()


def error_message_for_error_info(error_info: ErrorInfo) -> str:
    output_file = io.StringIO()
    print_error_info(FilePrinter(output_file), error_info)
    return output_file.getvalue()


def print_error_message_for_full_result(printer: FilePrinter, the_full_result: FullExeResult):
    main_blocks_renderer = full_exec_result.FullExeResultRenderer(the_full_result)

    print_major_blocks(main_blocks_renderer, printer)


def print_error_info(printer: FilePrinter, error_info: ErrorInfo):
    main_blocks_renderer = ErrorInfoRenderer(error_info)
    print_major_blocks(main_blocks_renderer, printer)


def print_major_blocks(blocks_renderer: SequenceRenderer[MajorBlock],
                       printer: FilePrinter):
    document_renderer = rend.DocumentR(blocks_renderer)

    print.print_document(document_renderer.render(),
                         printer)
