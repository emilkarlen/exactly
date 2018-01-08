import io
import pathlib

from exactly_lib.execution import full_execution
from exactly_lib.execution.result import FailureInfoVisitor, PhaseFailureInfo, InstructionFailureInfo
from exactly_lib.help_texts import misc_texts
from exactly_lib.help_texts.formatting import SectionName
from exactly_lib.help_texts.test_case.phase_names_plain import SECTION_CONCEPT_NAME
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.test_case import error_description
from exactly_lib.util import line_source, error_message_format
from exactly_lib.util.line_source import LinesInFile, SourceLocationPath
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
    _output_location(printer,
                     error_info.file,
                     error_info.maybe_section_name,
                     error_info.source,
                     None,
                     SECTION_CONCEPT_NAME)
    _ErrorDescriptionDisplayer(printer).visit(error_info.description)


def _output_location(printer: FilePrinter,
                     file: pathlib.Path,
                     section_name: str,
                     source: line_source.LineSequence,
                     description: str,
                     section_presentation_type_name: str):
    has_output_header = False
    if file:
        printer.write_line('File: ' + _file_str(file))
        has_output_header = True
    if section_name:
        printer.write_line('In ' + SectionName(section_name).syntax)
        has_output_header = True
    if source:
        if has_output_header:
            printer.write_empty_line()
        printer.write_line(error_message_format.source_line_sequence(source))
        has_output_header = True
    if description:
        printer.write_line('\nDescribed as "{}"'.format(description))
        has_output_header = True

    if has_output_header:
        printer.write_empty_line()


def output_location2(printer: FilePrinter,
                     source_info: LinesInFile,
                     section_name: str,
                     description: str,
                     section_presentation_type_name: str):
    if source_info is None:
        return _output_location(printer,
                                None,
                                section_name,
                                None,
                                description,
                                section_presentation_type_name)
    else:
        return _output_location(printer,
                                source_info.file_path,
                                section_name,
                                source_info.lines,
                                description,
                                section_presentation_type_name)


def output_location3(printer: FilePrinter,
                     source_location: SourceLocationPath,
                     section_name: str,
                     description: str,
                     section_presentation_type_name: str):
    if source_location is None:
        return output_location2(printer,
                                None,
                                section_name,
                                description,
                                section_presentation_type_name)
    source_info = None
    if source_location.location is not None:
        source_info = LinesInFile(source_location.location.source,
                                  source_location.location.file_path)
    return output_location2(printer,
                            source_info,
                            section_name,
                            description,
                            section_presentation_type_name)


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
        output_location3(self.out,
                         None,
                         failure_info.phase_step.phase.identifier,
                         None,
                         SECTION_CONCEPT_NAME)

    def _visit_instruction_failure(self, failure_info: InstructionFailureInfo):
        output_location3(self.out,
                         failure_info.source_location,
                         failure_info.phase_step.phase.identifier,
                         failure_info.element_description,
                         SECTION_CONCEPT_NAME)


def _file_str(path: pathlib.Path) -> str:
    if not path.is_absolute():
        return str(path)
    cwd = pathlib.Path.cwd().resolve()
    try:
        return str(path.relative_to(cwd))
    except ValueError:
        return str(path)
