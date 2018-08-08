from typing import Sequence, Dict, Optional

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedSectionElement
from exactly_lib.section_document.source_location import FileSystemLocationInfo


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

        :param fs_location_info: Information about the location of the source file being parsed
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