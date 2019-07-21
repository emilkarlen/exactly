import io
import pathlib
from typing import Optional, List, Sequence

from exactly_lib.common.report_rendering import print
from exactly_lib.common.report_rendering.source_location import SourceLocationPathRenderer, SourceLinesBlockRenderer
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.execution.failure_info import InstructionFailureInfo, PhaseFailureInfo, FailureInfoVisitor
from exactly_lib.execution.full_execution.result import FullExeResult
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.test_case import error_description
from exactly_lib.util.file_printables import print_to_string
from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.simple_textstruct import structure as struct
from exactly_lib.util.simple_textstruct.rendering import component_renderers as rend, renderer_combinators as comb
from exactly_lib.util.simple_textstruct.rendering.components import SequenceRenderer, MajorBlocksRenderer
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement, StringLineObject, \
    PreFormattedStringLineObject


def error_message_for_full_result(the_full_result: FullExeResult) -> str:
    output_file = io.StringIO()
    print_error_message_for_full_result(FilePrinter(output_file), the_full_result)
    return output_file.getvalue()


def error_message_for_error_info(error_info: ErrorInfo) -> str:
    output_file = io.StringIO()
    print_error_info(FilePrinter(output_file), error_info)
    return output_file.getvalue()


def print_error_message_for_full_result(printer: FilePrinter, the_full_result: FullExeResult):
    main_blocks_renderer = FullExeResultRenderer(the_full_result)

    print_major_blocks(main_blocks_renderer, printer)


def print_error_info(printer: FilePrinter, error_info: ErrorInfo):
    main_blocks_renderer = ErrorInfoRenderer(error_info)
    print_major_blocks(main_blocks_renderer, printer)


def print_major_blocks(blocks_renderer: Renderer[Sequence[MajorBlock]],
                       printer: FilePrinter):
    document_renderer = rend.DocumentR(blocks_renderer)

    print.print_document(document_renderer.render(),
                         printer)


def location_blocks_renderer(source_location: Optional[SourceLocationPath],
                             section_name: Optional[str],
                             description: Optional[str]) -> Renderer[Sequence[MajorBlock]]:
    return comb.SingletonSequenceR(
        rend.MajorBlockR(
            location_minor_blocks_renderer(source_location,
                                           section_name,
                                           description)
        )
    )


def location_minor_blocks_renderer(source_location: Optional[SourceLocationPath],
                                   section_name: Optional[str],
                                   description: Optional[str]) -> Renderer[Sequence[MinorBlock]]:
    minor_blocks_renderer = _location_path_and_source_blocks(source_location)
    if section_name is not None:
        minor_blocks_renderer = comb.PrependFirstMinorBlockR(_InSectionNameRenderer(section_name),
                                                             minor_blocks_renderer)
    return comb.ConcatenationR([
        minor_blocks_renderer,
        _OptionalDescriptionRenderer(description),
    ])


def source_lines_in_section_block_renderer(section_name: str,
                                           source_lines: Sequence[str],
                                           ) -> Renderer[Sequence[MinorBlock]]:
    return comb.SequenceR([
        rend.MinorBlockR(_InSectionNameRenderer(section_name)),
        SourceLinesBlockRenderer(source_lines),
    ])


def _location_path_and_source_blocks(source_location: Optional[SourceLocationPath]) -> Renderer[Sequence[MinorBlock]]:
    if source_location is None:
        return comb.SequenceR([])
    else:
        referrer_location = pathlib.Path('.')
        return SourceLocationPathRenderer(referrer_location,
                                          source_location)


class ErrorInfoRenderer(MajorBlocksRenderer):
    def __init__(self, error_info: ErrorInfo):
        self._error_info = error_info

    def render(self) -> Sequence[MajorBlock]:
        renderers = [
            location_blocks_renderer(self._error_info.source_location_path,
                                     self._error_info.maybe_section_name,
                                     None),
            ErrorDescriptionRenderer(self._error_info.description),
        ]

        return comb.ConcatenationR(renderers).render()


class FullExeResultRenderer(MajorBlocksRenderer):
    def __init__(self, full_result: FullExeResult):
        self._result = full_result

    def render(self) -> Sequence[MajorBlock]:
        if not self._result.is_failure:
            return []
        else:
            return self._rendition_for_failure()

    def _rendition_for_failure(self) -> Sequence[MajorBlock]:
        failure_info = self._result.failure_info
        major_blocks = list(_SourceDisplayer().visit(failure_info).render())

        failure_details = failure_info.failure_details
        if failure_details.is_only_failure_message:
            ed = error_description.of_message(failure_details.failure_message)
        else:
            ed = error_description.of_exception(failure_details.exception,
                                                failure_details.failure_message)

        major_blocks += _ErrorDescriptionDisplayer().visit(ed)

        return major_blocks


class ErrorDescriptionRenderer(MajorBlocksRenderer):
    def __init__(self, description: error_description.ErrorDescription):
        self._description = description

    def render(self) -> Sequence[MajorBlock]:
        return _ErrorDescriptionDisplayer().visit(self._description)


class _ErrorDescriptionDisplayer(error_description.ErrorDescriptionVisitor[Sequence[MajorBlock]]):
    def _visit_message(self, ed: error_description.ErrorDescriptionOfMessage) -> Sequence[MajorBlock]:
        message_blocks = self._message_blocks(ed)
        return (
            [MajorBlock(message_blocks)]
            if message_blocks
            else []
        )

    def _visit_exception(self, ed: error_description.ErrorDescriptionOfException) -> Sequence[MajorBlock]:
        minor_blocks = self._message_blocks(ed)
        minor_blocks.append(
            struct.minor_block_from_lines([
                struct.StringLineObject('Exception:'),
                struct.PreFormattedStringLineObject(str(ed.exception), False),
            ])
        )

        return [MajorBlock(minor_blocks)]

    def _visit_external_process_error(self, ed: error_description.ErrorDescriptionOfExternalProcessError
                                      ) -> Sequence[MajorBlock]:
        minor_blocks = self._message_blocks(ed)
        lines = [struct.StringLineObject(misc_texts.EXIT_CODE.singular.capitalize() + ': ' +
                                         str(ed.external_process_error.exit_code))]

        if ed.external_process_error.stderr_output:
            lines.append(struct.PreFormattedStringLineObject(ed.external_process_error.stderr_output, False))

        minor_blocks.append(
            struct.minor_block_from_lines(lines)
        )

        return [MajorBlock(minor_blocks)]

    def _message_blocks(self, ed: error_description.ErrorDescription) -> List[MinorBlock]:
        if ed.message is None:
            return []
        else:
            message_as_str = print_to_string(ed.message)
            return [
                struct.minor_block_from_lines([struct.PreFormattedStringLineObject(message_as_str, False)])
            ]


class _SourceDisplayer(FailureInfoVisitor[Renderer[Sequence[MajorBlock]]]):
    def _visit_phase_failure(self, failure_info: PhaseFailureInfo) -> Renderer[Sequence[MajorBlock]]:
        return location_blocks_renderer(None,
                                        failure_info.phase_step.phase.identifier,
                                        None)

    def _visit_instruction_failure(self, failure_info: InstructionFailureInfo) -> Renderer[Sequence[MajorBlock]]:
        return location_blocks_renderer(failure_info.source_location,
                                        failure_info.phase_step.phase.identifier,
                                        failure_info.element_description)


class _InSectionNameRenderer(SequenceRenderer[LineElement]):
    def __init__(self, section_name: str):
        self._section_name = section_name

    def render(self) -> Sequence[LineElement]:
        return [
            LineElement(StringLineObject('In ' + SectionName(self._section_name).syntax))
        ]


class _OptionalDescriptionRenderer(SequenceRenderer[MinorBlock]):
    def __init__(self, description: Optional[str]):
        self._description = description

    def render(self) -> Sequence[MinorBlock]:
        if self._description is None:
            return []
        else:
            return [
                MinorBlock([
                    LineElement(PreFormattedStringLineObject(_description_str(self._description), False))
                ])
            ]


def _description_str(description: str) -> str:
    return 'Described as "{}"'.format(description)
