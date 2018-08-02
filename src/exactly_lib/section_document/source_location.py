from pathlib import Path
from typing import Sequence, Optional

from exactly_lib.util.line_source import Line, line_sequence_from_line, LineSequence


class SourceLocation(tuple):
    """A location in a file."""

    def __new__(cls,
                source: LineSequence,
                file_path_rel_referrer: Optional[Path]):
        """
        :param source: See corresponding getter
        :param file_path_rel_referrer: See corresponding getter
        """
        return tuple.__new__(cls, (source, file_path_rel_referrer))

    @property
    def source(self) -> LineSequence:
        """
        :return: None iff source if not relevant
        """
        return self[0]

    @property
    def file_path_rel_referrer(self) -> Optional[Path]:
        """
        :return: None iff source does not originate from a file
        The path is relative the directory that contains the referring file - the file
        that includes this file (in case of file inclusion), or the PWD, e.g. for a
        CLI argument case file.
        """
        return self[1]


class SourceLocationPath(tuple):
    """A location in a file, with file inclusion chain info."""

    def __new__(cls,
                location: SourceLocation,
                file_inclusion_chain: Sequence[SourceLocation]):
        return tuple.__new__(cls, (location, file_inclusion_chain))

    @property
    def location(self) -> SourceLocation:
        return self[0]

    @property
    def file_inclusion_chain(self) -> Sequence[SourceLocation]:
        return self[1]


def source_location_path_of(file_path: Path,
                            line: Line) -> SourceLocationPath:
    """
    :return: None iff file_path and line is None
    """
    if file_path is None and line is None:
        return None
    line_sequence = None
    if line:
        line_sequence = line_sequence_from_line(line)
    return source_location_path_without_inclusions(
        SourceLocation(line_sequence,
                       file_path)
    )


def source_location_path_without_inclusions(location: SourceLocation) -> SourceLocationPath:
    return SourceLocationPath(location, ())


def source_location_path_of_non_empty_location_path(location_path: Sequence[SourceLocation]) -> SourceLocationPath:
    return SourceLocationPath(location_path[-1],
                              location_path[:-1])


class FileLocationInfo(tuple):
    """Information about the location and inclusion chain of a file."""

    def __new__(cls,
                abs_path_of_dir_containing_root_file: Path,
                file_path_rel_referrer: Optional[Path] = None,
                file_inclusion_chain: Sequence[SourceLocation] = (),
                abs_path_of_dir_containing_file: Optional[Path] = None):
        return tuple.__new__(cls, (abs_path_of_dir_containing_root_file,
                                   file_path_rel_referrer,
                                   file_inclusion_chain,
                                   abs_path_of_dir_containing_file))

    @property
    def file_path_rel_referrer(self) -> Optional[Path]:
        return self[1]

    @property
    def file_inclusion_chain(self) -> Sequence[SourceLocation]:
        return self[2]

    @property
    def abs_path_of_dir_containing_file(self) -> Optional[Path]:
        return self[3]

    @property
    def abs_path_of_dir_containing_root_file(self) -> Path:
        """Absolute path of the dir containing the first file in the inclusion chain;
        or the dir that is regarded to have this property, if there is no root file
        (i.e. the root is stdin or equivalent).
        """
        return self[0]

    def source_location_of(self, source: LineSequence) -> SourceLocation:
        return SourceLocation(source, self.file_path_rel_referrer)

    def source_location_path(self, source: LineSequence) -> SourceLocationPath:
        return SourceLocationPath(self.source_location_of(source),
                                  self.file_inclusion_chain)

    def location_path_of(self, source: LineSequence) -> Sequence[SourceLocation]:
        return list(self.file_inclusion_chain) + [self.source_location_of(source)]


class FileSystemLocationInfo(tuple):
    def __new__(cls, current_source_file: FileLocationInfo):
        return tuple.__new__(cls, (current_source_file,))

    @property
    def current_source_file(self) -> FileLocationInfo:
        """Information about the source file that contains the instruction being parsed"""
        return self[0]


class SourceLocationInfo(tuple):
    """Information about the location and inclusion chain of source lines in file."""

    def __new__(cls,
                abs_path_of_dir_containing_root_file: Path,
                source_location_path: SourceLocationPath,
                abs_path_of_dir_containing_file: Optional[Path] = None):
        return tuple.__new__(cls, (abs_path_of_dir_containing_root_file,
                                   source_location_path,
                                   abs_path_of_dir_containing_file))

    @property
    def abs_path_of_dir_containing_root_file(self) -> Path:
        return self[0]

    @property
    def source_location_path(self) -> SourceLocationPath:
        return self[1]

    @property
    def abs_path_of_dir_containing_file(self) -> Optional[Path]:
        return self[2]
