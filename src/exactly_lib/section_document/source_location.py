from pathlib import Path
from typing import Sequence, Optional

from exactly_lib.util.line_source import Line, line_sequence_from_line, LineSequence


class SourceLocation(tuple):
    """A location in a file."""

    def __new__(cls,
                source: Optional[LineSequence],
                file_path_rel_referrer: Optional[Path]):
        """
        :param source: See corresponding getter
        :param file_path_rel_referrer: See corresponding getter
        """
        return tuple.__new__(cls, (source, file_path_rel_referrer))

    @property
    def source(self) -> Optional[LineSequence]:
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

    def __str__(self):
        return """\
file_path_rel_referrer={}
source={}""".format(self.file_path_rel_referrer,
                    self.source)


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


def source_location_path_of(file_path: Optional[Path],
                            line: Optional[Line]) -> Optional[SourceLocationPath]:
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


class WithFileLocationInfo:
    """Has information about a file location, with file inclusions."""

    def __init__(self, abs_path_of_dir_containing_first_file_path: Path):
        self._abs_path_of_dir_containing_root_file_path = abs_path_of_dir_containing_first_file_path

    @property
    def file_path_rel_referrer(self) -> Optional[Path]:
        raise NotImplementedError('abstract method')

    @property
    def file_inclusion_chain(self) -> Sequence[SourceLocation]:
        raise NotImplementedError('abstract method')

    @property
    def abs_path_of_dir_containing_first_file_path(self) -> Path:
        """Absolute path of the dir containing the first referenced file path
        (first referenced file corresponds to the file path argument given to the parser);
        or the dir that is regarded to have this property, if there is no root file
        (i.e. the root is stdin or equivalent).
        """
        return self._abs_path_of_dir_containing_root_file_path

    @property
    def abs_path_of_dir_containing_last_file_base_name(self) -> Path:
        ret_val = self.abs_path_of_dir_containing_first_file_path
        file_path_rel_referrer_list = ([source_location.file_path_rel_referrer
                                        for source_location in self.file_inclusion_chain
                                        ] +
                                       [self.file_path_rel_referrer])
        for file_path_rel_referrer in file_path_rel_referrer_list:
            if file_path_rel_referrer is not None:
                ret_val = ret_val / file_path_rel_referrer.parent
        return ret_val


class SourceLocationInfo(WithFileLocationInfo):
    """Information about the location and inclusion chain of source lines in file."""

    def __init__(self,
                 abs_path_of_dir_containing_first_file_path: Path,
                 source_location_path: SourceLocationPath):
        super().__init__(abs_path_of_dir_containing_first_file_path)
        self._source_location_path = source_location_path

    @property
    def file_path_rel_referrer(self) -> Optional[Path]:
        return self.source_location_path.location.file_path_rel_referrer

    @property
    def file_inclusion_chain(self) -> Sequence[SourceLocation]:
        return self.source_location_path.file_inclusion_chain

    @property
    def source_location_path(self) -> SourceLocationPath:
        return self._source_location_path


class FileLocationInfo(WithFileLocationInfo):
    """Information about the location and inclusion chain of a file."""

    def __init__(self,
                 abs_path_of_dir_containing_first_file_path: Path,
                 file_path_rel_referrer: Optional[Path] = None,
                 file_inclusion_chain: Sequence[SourceLocation] = ()):
        super().__init__(abs_path_of_dir_containing_first_file_path)
        self._file_path_rel_referrer = file_path_rel_referrer
        self._file_inclusion_chain = file_inclusion_chain

    @property
    def file_path_rel_referrer(self) -> Optional[Path]:
        return self._file_path_rel_referrer

    @property
    def file_inclusion_chain(self) -> Sequence[SourceLocation]:
        return self._file_inclusion_chain

    def source_location_of(self, source: LineSequence) -> SourceLocation:
        return SourceLocation(source, self.file_path_rel_referrer)

    def source_location_path(self, source: LineSequence) -> SourceLocationPath:
        return SourceLocationPath(self.source_location_of(source),
                                  self.file_inclusion_chain)

    def location_path_of(self, source: LineSequence) -> Sequence[SourceLocation]:
        return list(self.file_inclusion_chain) + [self.source_location_of(source)]

    def source_location_info_for(self, source: LineSequence) -> SourceLocationInfo:
        return SourceLocationInfo(self.abs_path_of_dir_containing_first_file_path,
                                  self.source_location_path(source))


class FileSystemLocationInfo(tuple):
    def __new__(cls, current_source_file: FileLocationInfo):
        return tuple.__new__(cls, (current_source_file,))

    @property
    def current_source_file(self) -> FileLocationInfo:
        """Information about the source file that contains the instruction being parsed"""
        return self[0]


def _abs_path_of_dir_containing_file(abs_path_of_dir_containing_root_file: Path,
                                     final_file: Optional[Path],
                                     file_inclusion_chain: Sequence[SourceLocation],
                                     ) -> Path:
    ret_val = abs_path_of_dir_containing_root_file
    file_path_rel_referrer_list = ([source_location.file_path_rel_referrer
                                    for source_location in file_inclusion_chain
                                    ] +
                                   [final_file])
    for file_path_rel_referrer in file_path_rel_referrer_list:
        if file_path_rel_referrer is not None:
            ret_val = ret_val / file_path_rel_referrer.parent
    return ret_val
