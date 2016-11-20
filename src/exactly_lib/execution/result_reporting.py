import io
import pathlib

from exactly_lib.execution import full_execution
from exactly_lib.execution.result import FailureInfoVisitor, PhaseFailureInfo, InstructionFailureInfo
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.test_case import error_description
from exactly_lib.util import line_source
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
        if failure_info.failure_details.is_only_failure_message:
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
                    error_info.file,
                    error_info.maybe_section_name,
                    error_info.line)
    _ErrorDescriptionDisplayer(printer).visit(error_info.description)


def output_location(printer: FilePrinter,
                    file: pathlib.Path,
                    section_name: str,
                    line: line_source.Line,
                    section_presentation_type_name: str = 'phase'):
    has_output_header = False
    if file:
        printer.write_line('File: ' + str(file))
        has_output_header = True
    if section_name:
        printer.write_line('In %s "%s"' % (section_presentation_type_name, section_name))
        has_output_header = True
    if line:
        printer.write_line('Line {}: `{}\''.format(line.line_number, line.text))
        has_output_header = True

    if has_output_header:
        printer.write_line('')


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
        self.out.write_line('Exit code: ' + str(ed.external_process_error.exit_code))
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
                        None,
                        failure_info.phase_step.phase.identifier,
                        failure_info.source_line)
