import io
import pathlib
from typing import Optional, List, Tuple

from exactly_lib.common.err_msg import rendering
from exactly_lib.common.err_msg.definitions import Blocks, Block
from exactly_lib.common.err_msg.source_location import default_formatter
from exactly_lib.common.err_msg.utils import prefix_first_block
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.execution.failure_info import InstructionFailureInfo, PhaseFailureInfo, FailureInfoVisitor
from exactly_lib.execution.full_execution.result import FullExeResult
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.test_case import error_description
from exactly_lib.util.std import FilePrinter


def error_message_for_full_result(the_full_result: FullExeResult) -> str:
    output_file = io.StringIO()
    print_error_message_for_full_result(FilePrinter(output_file), the_full_result)
    return output_file.getvalue()


def print_error_message_for_full_result(printer: FilePrinter, the_full_result: FullExeResult):
    if the_full_result.is_failure:
        failure_info = the_full_result.failure_info
        _SourceDisplayer(printer).visit(failure_info)
        failure_details = failure_info.failure_details
        if failure_details.is_only_failure_message:
            ed = error_description.of_message(failure_details.failure_message)
        else:
            ed = error_description.of_exception(failure_details.exception,
                                                failure_details.failure_message)
        _ErrorDescriptionDisplayer(printer).visit(ed)


def error_message_for_error_info(error_info: ErrorInfo) -> str:
    output_file = io.StringIO()
    print_error_info(FilePrinter(output_file), error_info)
    return output_file.getvalue()


def print_error_info(printer: FilePrinter, error_info: ErrorInfo):
    output_location(printer,
                    error_info.source_location_path,
                    error_info.maybe_section_name,
                    None)
    _ErrorDescriptionDisplayer(printer).visit(error_info.description)


def output_location(printer: FilePrinter,
                    source_location: Optional[SourceLocationPath],
                    section_name: Optional[str],
                    description: Optional[str],
                    append_blank_line_if_any_output: bool = True):
    location, source = location_path_and_source_blocks(source_location)
    output_location_with_source_block(
        printer,
        location,
        source,
        section_name,
        description,
        append_blank_line_if_any_output
    )


def location_path_and_source_blocks(source_location: Optional[SourceLocationPath]) -> Tuple[Blocks, Blocks]:
    if source_location is None:
        return [], []
    else:
        referrer_location = pathlib.Path('.')
        formatter = default_formatter()
        return formatter.location_path_and_source_blocks(referrer_location,
                                                         source_location)


def source_lines_blocks(source: Optional[List[str]]) -> Blocks:
    if source is None:
        return []
    else:
        formatter = default_formatter()
        return [
            formatter.source_lines(source)
        ]


def output_location_with_source_block(printer: FilePrinter,
                                      location: Blocks,
                                      source: Blocks,
                                      section_name: Optional[str],
                                      description: Optional[str],
                                      append_blank_line_if_any_output: bool = True):
    blocks = location

    if section_name:
        blocks = prefix_first_block(_section_name_block(section_name), blocks)

    blocks += source

    blocks += _description_blocks(description)

    if blocks:
        printer.write_line(rendering.blocks_as_str(blocks))
        if append_blank_line_if_any_output:
            printer.write_empty_line()


class _ErrorDescriptionDisplayer(error_description.ErrorDescriptionVisitor):
    def __init__(self,
                 out: FilePrinter):
        self.out = out

    def _visit_message(self, ed: error_description.ErrorDescriptionOfMessage):
        self.out.write_line_if_present(ed.message)

    def _visit_exception(self, ed: error_description.ErrorDescriptionOfException):
        self.out.write_line_if_present(ed.message)
        self.out.write_line('Exception:')
        self.out.write_line(str(ed.exception))

    def _visit_external_process_error(self, ed: error_description.ErrorDescriptionOfExternalProcessError):
        self.out.write_line_if_present(ed.message)
        self.out.write_line(misc_texts.EXIT_CODE.singular.capitalize() + ': ' +
                            str(ed.external_process_error.exit_code))
        if ed.external_process_error.stderr_output:
            self.out.write_line(ed.external_process_error.stderr_output)


class _SourceDisplayer(FailureInfoVisitor):
    def __init__(self,
                 out: FilePrinter):
        self.out = out

    def _visit_phase_failure(self, failure_info: PhaseFailureInfo):
        output_location(self.out,
                        None,
                        failure_info.phase_step.phase.identifier,
                        None)

    def _visit_instruction_failure(self, failure_info: InstructionFailureInfo):
        output_location(self.out,
                        failure_info.source_location,
                        failure_info.phase_step.phase.identifier,
                        failure_info.element_description)


def _section_name_block(section_name: str) -> Block:
    return ['In ' + SectionName(section_name).syntax]


def _description_blocks(description: Optional[str]) -> Blocks:
    if description:
        return [
            ['Described as "{}"'.format(description)],
        ]
    else:
        return []
