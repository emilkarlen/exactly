import pathlib
from typing import Sequence, Dict, Optional

from exactly_lib.section_document import model
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedSectionElement


class DocumentParser:
    """
    Base class for parsers that parse a "plain file"
    (i.e., a file that do not need pre-processing).
    """

    def parse(self,
              source_file_path: Optional[pathlib.Path],
              file_reference_relativity_root_dir: pathlib.Path,
              source: ParseSource) -> model.Document:
        """
        :param source_file_path: None if the source is not a file.
        :param file_reference_relativity_root_dir: A directory that file reference paths are relative to.
        :param source: The source to parse - the contents of source_file_path, if the source is from a file.
        :raises ParseError The test case cannot be parsed.
        """
        raise NotImplementedError('abstract method')


class FileSystemLocationInfo(tuple):
    def __new__(cls, file_reference_relativity_root_dir: pathlib.Path):
        return tuple.__new__(cls, (file_reference_relativity_root_dir,))

    @property
    def file_reference_relativity_root_dir(self) -> pathlib.Path:
        """A directory that file reference paths are relative to"""
        return self[0]


class SectionElementParser:
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> Optional[ParsedSectionElement]:
        """
        May return None if source is recognized.
        Unrecognized source may also be reported by raising SourceError.

        The possibility to return None exists to help constructing parsers from parts -
        a return value of None means that some other parser may try to parse the same source,
        while a raised SourceError means that this parser recognizes the source (e.g. by
        being the name of an instruction), but that there is some syntax error related to
        the recognized element (e.g. instruction).

        :param source: Remaining source to parse

        :returns: None iff source is invalid / unrecognized. If None is returned, source must _not_
        have been consumed by this parser.
        :raises SourceError: The element cannot be parsed.
        """
        raise NotImplementedError('abstract method')


class SectionConfiguration(tuple):
    def __new__(cls,
                section_name: str,
                parser: SectionElementParser):
        return tuple.__new__(cls, (section_name, parser))

    @property
    def section_name(self) -> str:
        return self[0]

    @property
    def parser(self) -> SectionElementParser:
        return self[1]


class SectionsConfiguration:
    """
    Sections and their instruction parser.
    """

    def __init__(self,
                 parsers_for_named_sections: Sequence[SectionConfiguration],
                 default_section_name: str = None,
                 section_element_name_for_error_messages: str = 'section'):
        self.section_element_name_for_error_messages = section_element_name_for_error_messages
        self._parsers_for_named_sections = parsers_for_named_sections
        self._section2parser = {
            pfs.section_name: pfs.parser
            for pfs in parsers_for_named_sections
        }

        self.default_section_name = default_section_name
        if default_section_name is not None:
            if default_section_name not in self._section2parser:
                raise ValueError('The name of the default section "%s" does not correspond to any section: %s' %
                                 (default_section_name,
                                  str(self._section2parser.keys()))
                                 )

    def sections(self) -> Dict[str, SectionElementParser]:
        return self._section2parser

    def parser_for_section(self, section_name: str) -> SectionElementParser:
        return self._section2parser[section_name]

    def has_section(self, section_name: str) -> bool:
        return section_name in self._section2parser
