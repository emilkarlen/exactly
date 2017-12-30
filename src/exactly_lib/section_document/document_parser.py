import pathlib
from typing import Sequence, Dict, List

from exactly_lib.section_document import model
from exactly_lib.section_document import syntax
from exactly_lib.section_document.element_builder import SectionContentElementBuilder
from exactly_lib.section_document.exceptions import SourceError, FileSourceError, FileAccessError
from exactly_lib.section_document.model import SectionContentElement
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parser import ParsedSectionElement, ParsedSectionElementVisitor, \
    ParsedInstruction, ParsedNonInstructionElement, ParsedFileInclusionDirective
from exactly_lib.section_document.utils import new_for_file
from exactly_lib.util import line_source
from exactly_lib.util.line_source import SourceLocation


class DocumentParser:
    """
    Base class for parsers that parse a "plain file"
    (i.e., a file that do not need pre-processing).
    """

    def parse(self,
              source_file_path: pathlib.Path,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> model.Document:
        """
        :param source_file_path: None if the source is not a file.
        :param file_inclusion_relativity_root: A directory that file inclusion paths are relative to.
        :param source: The source to parse - the contents of source_file_path, if the source is from a file.
        :raises FileSourceError The test case cannot be parsed.
        """
        raise NotImplementedError()


class SectionElementParser:
    def parse(self,
              source: ParseSource,
              element_builder: SectionContentElementBuilder) -> ParsedSectionElement:
        """
        :raises FileSourceError The element cannot be parsed.
        """
        raise NotImplementedError()


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
            pfp.section_name: pfp.parser
            for pfp in parsers_for_named_sections
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


class _SectionsConfigurationInternal:
    """
    Sections and their instruction parser.
    """

    def __init__(self,
                 sections: Dict[str, SectionElementParser],
                 default_section_name: str = None,
                 section_element_name_for_error_messages: str = 'section'):
        self.section_element_name_for_error_messages = section_element_name_for_error_messages
        self._section2parser = sections

        self._parser_for_default_section = None
        self.default_section_name = default_section_name

    def parser_for_section(self, section_name: str) -> SectionElementParser:
        return self._section2parser[section_name]

    def has_section(self, section_name: str) -> bool:
        return section_name in self._section2parser


def new_parser_for(configuration: SectionsConfiguration) -> DocumentParser:
    return _DocumentParserForSectionsConfiguration(configuration)


def parse(configuration: SectionsConfiguration,
          source_file_path: pathlib.Path) -> model.Document:
    source_parser = new_parser_for(configuration)
    file_inclusion_relativity_root = source_file_path.parent
    source = read_source_file(source_file_path, [])
    return source_parser.parse(source_file_path, file_inclusion_relativity_root, source)


def read_source_file(file_path: pathlib.Path,
                     location_path: Sequence[SourceLocation]) -> ParseSource:
    try:
        return new_for_file(file_path)
    except OSError as ex:
        raise FileAccessError(file_path, str(ex), location_path)


class _DocumentParserForSectionsConfiguration(DocumentParser):
    def __init__(self, configuration: SectionsConfiguration):
        self._configuration = _SectionsConfigurationInternal(configuration.sections(),
                                                             configuration.default_section_name,
                                                             configuration.section_element_name_for_error_messages)

    def parse(self,
              source_file_path: pathlib.Path,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> model.Document:
        impl = _Impl(self._configuration,
                     SectionContentElementBuilder(source_file_path),
                     file_inclusion_relativity_root,
                     source)
        return _build_document(impl.apply())


class SectionContentsElementConstructor(ParsedSectionElementVisitor[model.SectionContentElement]):
    def __init__(self,
                 element_builder: SectionContentElementBuilder):
        self._element_builder = element_builder

    def visit_instruction_element(self, instruction: ParsedInstruction) -> model.SectionContentElement:
        return self._element_builder.new_instruction(instruction.source,
                                                     instruction.instruction_info.instruction,
                                                     instruction.instruction_info.description)

    def visit_non_instruction_element(self, non_instruction: ParsedNonInstructionElement
                                      ) -> model.SectionContentElement:
        return self._element_builder.new_non_instruction(non_instruction.source,
                                                         non_instruction.element_type)

    def visit_file_inclusion_directive(self, file_inclusion: ParsedFileInclusionDirective
                                       ) -> model.SectionContentElement:
        raise NotImplementedError('not implemented')


class _Impl:
    def __init__(self,
                 configuration: _SectionsConfigurationInternal,
                 element_builder: SectionContentElementBuilder,
                 file_inclusion_relativity_root: pathlib.Path,
                 document_source: ParseSource):
        self.configuration = configuration
        self._element_builder = element_builder
        self._file_inclusion_relativity_root = file_inclusion_relativity_root
        self._document_source = document_source
        self._current_line = self._get_current_line_or_none_if_is_at_eof()
        self._parser_for_current_section = None
        self._name_of_current_section = None
        self._elements_for_current_section = []
        self._section_name_2_element_list = {}
        self._element_constructor = SectionContentsElementConstructor(element_builder)

    @property
    def parser_for_current_section(self) -> SectionElementParser:
        return self._parser_for_current_section

    def apply(self) -> Dict[str, List[SectionContentElement]]:
        if self.is_at_eof():
            return {}
        if self.current_line_is_section_line():
            self.switch_section_according_to_last_section_line_and_consume_section_lines()
            self.read_rest_of_document_from_inside_section_or_at_eof()
        else:
            if self.configuration.default_section_name is not None:
                self.set_current_section(self.configuration.default_section_name)
                self.read_rest_of_document_from_inside_section_or_at_eof()
            else:
                self.skip_standard_comment_and_empty_lines()
                if not self.is_at_eof():
                    if self.current_line_is_section_line():
                        self.switch_section_according_to_last_section_line_and_consume_section_lines()
                        self.read_rest_of_document_from_inside_section_or_at_eof()
                    else:
                        msg = 'Instruction outside of {section}'.format(
                            section=self.configuration.section_element_name_for_error_messages)
                        raise FileSourceError(SourceError(self._current_line,
                                                          msg),
                                              None)
        return self._section_name_2_element_list

    def switch_section_according_to_last_section_line_and_consume_section_lines(self):
        """
        Precondition: Current line is a section-line
        Post condition: Current line is not a section-line.

        If there are many consecutive section lines, then all of these are consumed.
        """
        while not self.is_at_eof() and self.current_line_is_section_line():
            section_line = self._current_line
            section_name = self.extract_section_name_and_consume_line()
            if not self.has_section(section_name):
                msg = 'There is no {section} named "{name}"'.format(
                    section=self.configuration.section_element_name_for_error_messages,
                    name=section_name)
                raise FileSourceError(SourceError(section_line,
                                                  msg),
                                      None)
            self.set_current_section(section_name)

    def read_rest_of_document_from_inside_section_or_at_eof(self):
        while True:
            if self.is_at_eof():
                return
            self.read_section_elements_until_next_section_or_eof()
            if self.is_at_eof():
                return
            if self.current_line_is_section_line():
                self.switch_section_according_to_last_section_line_and_consume_section_lines()

    def read_section_elements_until_next_section_or_eof(self):
        while not self.is_at_eof() and not self.current_line_is_section_line():
            try:
                element = self.parse_element_at_current_line_using_current_section_element_parser()
            except SourceError as ex:
                raise FileSourceError(ex, self._name_of_current_section)
            self.add_element_to_current_section(element)

            self._current_line = self._get_current_line_or_none_if_is_at_eof()

    def parse_element_at_current_line_using_current_section_element_parser(self) -> model.SectionContentElement:
        parsed_element = self.parser_for_current_section.parse(self._document_source, self._element_builder)
        return self._element_constructor.visit(parsed_element)

    def add_element_to_current_section(self, element: model.SectionContentElement):
        self._elements_for_current_section.append(element)

    def extract_section_name_and_consume_line(self) -> str:
        try:
            section_name = syntax.extract_section_name_from_section_line(self._current_line.text)
        except ValueError as ex:
            raise FileSourceError(SourceError(self._current_line,
                                              str(ex)),
                                  None)
        self.move_one_line_forward()
        return section_name

    def set_current_section(self, section_name: str):
        self._name_of_current_section = section_name
        self._parser_for_current_section = self.configuration.parser_for_section(section_name)
        if section_name not in self._section_name_2_element_list:
            self._section_name_2_element_list[section_name] = []
        self._elements_for_current_section = self._section_name_2_element_list[section_name]

    def has_section(self, section_name: str) -> bool:
        return self.configuration.has_section(section_name)

    def move_one_line_forward(self):
        self._document_source.consume_current_line()
        self._current_line = self._get_current_line_or_none_if_is_at_eof()

    def is_at_eof(self) -> bool:
        return self._current_line is None

    def current_line_is_section_line(self) -> bool:
        return syntax.is_section_header_line(self._current_line.text)

    def skip_standard_comment_and_empty_lines(self):
        while not self.is_at_eof():
            if not self.current_line_is_comment_or_empty():
                break
            self.move_one_line_forward()

    def _get_current_line_or_none_if_is_at_eof(self) -> line_source.Line:
        return None \
            if self._document_source.is_at_eof \
            else self._document_source.current_line

    def current_line_is_comment_or_empty(self):
        return syntax.EMPTY_LINE_RE.match(self._current_line.text) or \
               syntax.COMMENT_LINE_RE.match(self._current_line.text)


def _build_document(sections: Dict[str, List[SectionContentElement]]) -> model.Document:
    return model.Document({
        section_name: model.SectionContents(tuple(elements))
        for section_name, elements in sections.items()
    })
