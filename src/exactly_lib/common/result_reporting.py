import io
import pathlib
from typing import Sequence

from exactly_lib.execution import full_execution
from exactly_lib.execution.result import FailureInfoVisitor, PhaseFailureInfo, InstructionFailureInfo
from exactly_lib.help_texts import misc_texts
from exactly_lib.help_texts.formatting import SectionName
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.test_case import error_description
from exactly_lib.util.error_message_format import source_line_sequence
from exactly_lib.util.line_source import SourceLocationPath, SourceLocation
from exactly_lib.util.std import FilePrinter


def error_message_for_full_result(the_full_result: full_execution.FullResult) -> str:
    output_file = io.StringIO()
    print_error_message_for_full_result(FilePrinter(output_file), the_full_result)
    return output_file.getvalue()


def print_error_message_for_full_result(printer: FilePrinter, the_full_result: full_execution.FullResult):
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


def _output_file_inclusion_chain(printer: FilePrinter,
                                 chain: Sequence[SourceLocation]):
    [
        print_file_inclusion_location(printer, location)
        for location in chain
    ]


def _output_location(printer: FilePrinter,
                     source_location: SourceLocation,
                     section_name: str,
                     description: str) -> bool:
    has_output_header = False
    if source_location and source_location.file_path:
        if source_location.source:
            printer.write_line(line_in_file(source_location))
        else:
            printer.write_line(_file_str(source_location.file_path))
        has_output_header = True
    if source_location and source_location.source:
        if has_output_header:
            printer.write_empty_line()
        printer.write_lines(source_line_sequence(source_location.source))
        has_output_header = True
    if description:
        printer.write_line('\nDescribed as "{}"'.format(description))
        has_output_header = True
    return has_output_header


def output_location(printer: FilePrinter,
                    source_location: SourceLocationPath,
                    section_name: str,
                    description: str):
    if section_name:
        printer.write_line('In ' + SectionName(section_name).syntax)
    if source_location is None:
        has_output = _output_location(printer,
                                      None,
                                      section_name,
                                      description)
    else:
        _output_file_inclusion_chain(printer, source_location.file_inclusion_chain)
        _output_location(printer,
                         source_location.location,
                         section_name,
                         description)
        has_output = True
    if has_output or section_name:
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


def _file_str(path: pathlib.Path) -> str:
    if not path.is_absolute():
        return str(path)
    cwd = pathlib.Path.cwd().resolve()
    try:
        return str(path.relative_to(cwd))
    except ValueError:
        return str(path)


def print_file_inclusion_location(printer: FilePrinter,
                                  location: SourceLocation):
    printer.write_line(line_in_file(location))
    [
        printer.write_line('  ' + line_source)
        for line_source in location.source.lines
    ]
    printer.write_empty_line()


def line_in_file(location: SourceLocation) -> str:
    return str(location.file_path) + ', line ' + str(location.source.first_line_number)
