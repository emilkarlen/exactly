import io
import pathlib
from typing import Optional

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
                    section_name: str,
                    description: str):
    referrer_location = pathlib.Path('.')
    formatter = default_formatter()

    section_name_block = []
    if section_name:
        section_name_block = _section_name_block(section_name)

    blocks = []
    if source_location is not None:
        blocks = formatter.source_location_path(referrer_location,
                                                source_location)
    blocks += _description_blocks(description)

    blocks = prefix_first_block(section_name_block, blocks)

    if blocks:
        printer.write_line(rendering.blocks_as_str(blocks))
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


def _description_blocks(description: str) -> Blocks:
    if description:
        return [
            ['Described as "{}"'.format(description)],
        ]
    else:
        return []
