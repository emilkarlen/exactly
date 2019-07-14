import os
from pathlib import Path
from typing import Sequence, Tuple, List, Optional

from exactly_lib.common.report_rendering.components import SequenceRenderer
from exactly_lib.section_document.source_location import SourceLocation, SourceLocationPath
from exactly_lib.util.ansi_terminal_color import FontStyle
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.structure import StringLinesObject, LineElement, MinorBlock, StringLineObject

SOURCE_LINES_ELEMENT_PROPERTIES = structure.ElementProperties(True, None)
SOURCE_LINES_BLOCK_PROPERTIES = structure.ElementProperties(False, None, FontStyle.BOLD)


def line_number(n: int) -> str:
    return ''.join(['line ', str(n)])


def source_location_path(referrer_location: Path,
                         source_location: SourceLocationPath) -> List[MinorBlock]:
    location = source_location.location
    source = location.source
    final_source_line_number = (
        None
        if source is None
        else source.first_line_number
    )

    ret_val = [
        _files_and_source_path_leading_to_final_source(
            referrer_location,
            source_location.file_inclusion_chain,
            final_source_line_number,
            location.file_path_rel_referrer,
        )
    ]
    if source is not None:
        ret_val.append(source_lines_block(source.lines))

    return ret_val


class SourceLocationPathRenderer(SequenceRenderer[MinorBlock]):
    def __init__(self,
                 referrer_location: Path,
                 source_location: SourceLocationPath):
        self._source_location = source_location
        self._referrer_location = referrer_location

    def render(self) -> Sequence[MinorBlock]:
        return source_location_path(self._referrer_location,
                                    self._source_location)


def source_lines_element(lines: Sequence[str]) -> LineElement:
    return LineElement(StringLinesObject(lines),
                       SOURCE_LINES_ELEMENT_PROPERTIES)


def source_lines_block(lines: Sequence[str]) -> MinorBlock:
    return MinorBlock(
        [source_lines_element(lines)],
        SOURCE_LINES_BLOCK_PROPERTIES
    )


def file_inclusion_chain(referrer_location: Path,
                         chain: Sequence[SourceLocation]) -> Tuple[List[LineElement], Path]:
    """
    :param referrer_location: The location of the file referring the first link
    in the chain

    :param chain: Sequence of location links (file inclusions)

    :return: (textual representation, referrer location of last link in chain)
    If the inclusion chain is empty, then the textual representation will also
    be empty.
    """

    def next_referrer_location(base: Path, link: SourceLocation) -> Path:
        if link.file_path_rel_referrer is None:
            return base
        else:
            return (referrer_location / link.file_path_rel_referrer).parent

    elements = []
    for link in chain:
        elements += _file_inclusion_location(referrer_location, link)
        referrer_location = next_referrer_location(referrer_location, link)

    return elements, referrer_location


def _file_inclusion_location(referrer_location: Path,
                             location: SourceLocation) -> List[LineElement]:
    return [
        _line_in_optional_file(referrer_location,
                               location.file_path_rel_referrer,
                               location.source.first_line_number),
        source_lines_element(location.source.lines),
    ]


def _line_in_optional_file(referrer_location: Path,
                           source_file: Optional[Path],
                           first_line_number: int) -> LineElement:
    if source_file is None:
        return LineElement(StringLineObject(line_number(first_line_number),
                                            False))
    else:
        path_str = os.path.normpath(str(referrer_location / source_file))
        return LineElement(StringLineObject(', '.join([path_str, line_number(first_line_number)]),
                                            False))


def _files_and_source_path_leading_to_final_source(referrer_location: Path,
                                                   the_file_inclusion_chain: Sequence[SourceLocation],
                                                   final_source_line_number: Optional[int],
                                                   final_file_path_rel_referrer: Optional[Path],
                                                   ) -> MinorBlock:
    lines, referrer_location = file_inclusion_chain(referrer_location,
                                                    the_file_inclusion_chain)

    if final_source_line_number is not None:
        lines += [
            _line_in_optional_file(referrer_location,
                                   final_file_path_rel_referrer,
                                   final_source_line_number)
        ]

    return MinorBlock(lines)
