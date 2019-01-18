import os
from pathlib import Path
from typing import Sequence, Tuple, Optional

from exactly_lib.common.err_msg.definitions import SOURCE_LINE_INDENT, Block, Blocks
from exactly_lib.section_document.source_location import SourceLocation, SourceLocationPath


class Formatter:
    def __init__(self, source_line_indent: str):
        self.source_line_indent = source_line_indent

    def source_location_path(self,
                             referrer_location: Path,
                             source_location: SourceLocationPath) -> Blocks:
        if source_location.location.source is None:
            return self._source_location_path__without_source(referrer_location,
                                                              source_location)
        else:
            return self._source_location_path__with_source(referrer_location,
                                                           source_location)

    def location_path_and_source_blocks(self,
                                        referrer_location: Path,
                                        source_location: SourceLocationPath) -> Tuple[Blocks, Blocks]:
        if source_location.location.source is None:
            return (
                self._source_location_path__without_source(referrer_location,
                                                           source_location),
                []
            )
        else:
            blocks = self._source_location_path__with_source(referrer_location, source_location)
            return [blocks[0]], [blocks[1]]

    def file_inclusion_chain(self,
                             referrer_location: Path,
                             chain: Sequence[SourceLocation]) -> Tuple[Block, Path]:
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

        lines = []
        for link in chain:
            lines += self.file_inclusion_location(referrer_location, link)
            referrer_location = next_referrer_location(referrer_location, link)

        return lines, referrer_location

    def file_inclusion_location(self,
                                referrer_location: Path,
                                location: SourceLocation) -> Block:
        lines = [
            line_in_optional_file(referrer_location,
                                  location.file_path_rel_referrer,
                                  location.source.first_line_number)
        ]

        lines += self.source_lines(location.source.lines)

        return lines

    def source_lines(self, lines: Sequence[str]) -> Block:
        return [
            self.source_line_indent + source_line
            for source_line in lines
        ]

    def _source_location_path__with_source(self,
                                           referrer_location: Path,
                                           source_location: SourceLocationPath) -> Blocks:
        location = source_location.location

        files_and_inclusions_block = self._files_and_source_path_leading_to_final_source(
            referrer_location,
            source_location.file_inclusion_chain,
            location.source.first_line_number,
            location.file_path_rel_referrer,
        )

        source_block = self.source_lines(location.source.lines)

        return [
            files_and_inclusions_block,
            source_block,
        ]

    def _source_location_path__without_source(self,
                                              referrer_location: Path,
                                              source_location: SourceLocationPath) -> Blocks:
        return [
            self._files_and_source_path_leading_to_final_source(
                referrer_location,
                source_location.file_inclusion_chain,
                None,
                source_location.location.file_path_rel_referrer,
            )
        ]

    def _files_and_source_path_leading_to_final_source(self,
                                                       referrer_location: Path,
                                                       file_inclusion_chain: Sequence[SourceLocation],
                                                       final_source_line_number: Optional[int],
                                                       final_file_path_rel_referrer: Optional[Path],
                                                       ) -> Block:
        files_and_inclusions_block, referrer_location = \
            self.file_inclusion_chain(referrer_location,
                                      file_inclusion_chain)

        if final_source_line_number is not None:
            files_and_inclusions_block += [
                line_in_optional_file(referrer_location,
                                      final_file_path_rel_referrer,
                                      final_source_line_number)
            ]

        return files_and_inclusions_block


def line_in_optional_file(referrer_location: Path,
                          source_file: Optional[Path],
                          first_line_number: int) -> str:
    if source_file is None:
        return line_number(first_line_number)
    else:
        path_str = os.path.normpath(str(referrer_location / source_file))
        return path_str + ', ' + line_number(first_line_number)


def line_in_file(source_file: Path,
                 first_line_number: int) -> str:
    path_str = os.path.normpath(str(source_file))
    return path_str + ', line ' + str(first_line_number)


def default_formatter() -> Formatter:
    return Formatter(SOURCE_LINE_INDENT)


def line_number(n: int) -> str:
    return 'line ' + str(n)
