import pathlib
from typing import Optional, List

from exactly_lib.common.err_msg import rendering
from exactly_lib.common.err_msg.definitions import Blocks, Block
from exactly_lib.common.err_msg.source_location import default_formatter
from exactly_lib.common.err_msg.utils import prefix_first_block
from exactly_lib.common.report_rendering.trace_doc import Renderer, SequenceRenderer
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.execution.failure_info import InstructionFailureInfo, PhaseFailureInfo, FailureInfoVisitor
from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.test_case import error_description
from exactly_lib.test_case_utils.err_msg.trace_doc import combinators
from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock


def output_location(source_location: Optional[SourceLocationPath],
                    section_name: Optional[str],
                    description: Optional[str]) -> Renderer[MajorBlock]:
    location, source = location_path_and_source_blocks(source_location)
    output_location_with_source_block(
        printer,
        location,
        source,
        section_name,
        description,
        append_blank_line_if_any_output
    )


def location_path_and_source_blocks(source_location: Optional[SourceLocationPath]) -> SequenceRenderer[MinorBlock]:
    if source_location is None:
        return combinators.ASequence([])
    else:
        referrer_location = pathlib.Path('.')
        formatter = default_formatter()
        return combinators.ASequence([

        ])
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
        self._output_message_line_if_present(ed)

    def _visit_exception(self, ed: error_description.ErrorDescriptionOfException):
        self._output_message_line_if_present(ed)
        self.out.write_line('Exception:')
        self.out.write_line(str(ed.exception))

    def _visit_external_process_error(self, ed: error_description.ErrorDescriptionOfExternalProcessError):
        self._output_message_line_if_present(ed)
        self.out.write_line(misc_texts.EXIT_CODE.singular.capitalize() + ': ' +
                            str(ed.external_process_error.exit_code))
        if ed.external_process_error.stderr_output:
            self.out.write_line(ed.external_process_error.stderr_output)

    def _output_message_line_if_present(self, ed: error_description.ErrorDescription):
        if ed.message is not None:
            ed.message.print_on(self.out)
            self.out.write_empty_line()


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
