import pathlib
from typing import Sequence, Dict, List, Optional

from exactly_lib.section_document import model
from exactly_lib.section_document import syntax
from exactly_lib.section_document.element_builder import SectionContentElementBuilder
from exactly_lib.section_document.exceptions import SourceError, FileSourceError, FileAccessError, \
    new_source_error_of_single_line
from exactly_lib.section_document.model import SectionContentElement
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedSectionElementVisitor, \
    ParsedInstruction, ParsedNonInstructionElement, ParsedFileInclusionDirective
from exactly_lib.section_document.parsing_configuration import SectionElementParser, SectionsConfiguration, \
    DocumentParser, FileSystemLocationInfo
from exactly_lib.section_document.utils import new_for_file
from exactly_lib.util import line_source
from exactly_lib.util.line_source import SourceLocation


class DocumentParserForSectionsConfiguration(DocumentParser):
    def __init__(self, configuration: SectionsConfiguration):
        self._configuration = internal_conf_of(configuration)

    def parse(self,
              source_file_path: Optional[pathlib.Path],
              file_reference_relativity_root_dir: pathlib.Path,
              source: ParseSource) -> model.Document:
        return parse_source(self._configuration,
                            SectionContentElementBuilder(source_file_path, []),
                            file_reference_relativity_root_dir,
                            source)


class _SectionsConfigurationInternal:
    """
    Sections and their instruction parser.
    """

    def __init__(self,
                 sections: Dict[str, SectionElementParser],
                 default_section_name: str = None,
                 section_element_name_for_error_messages: str = 'section'):
        self.section_element_name_for_error_messages = section_element_name_for_error_messages
        self.section2parser = sections

        self._parser_for_default_section = None
        self.default_section_name = default_section_name

    def parser_for_section(self, section_name: str) -> SectionElementParser:
        return self.section2parser[section_name]

    def has_section(self, section_name: str) -> bool:
        return section_name in self.section2parser


def parse(configuration: SectionsConfiguration,
          source_file_path: pathlib.Path) -> model.Document:
    raw_doc = parse_file(internal_conf_of(configuration),
                         source_file_path,
                         [],
                         resolve_file_reference_relativity_root_dir(pathlib.Path.cwd(), []),
                         [])
    return build_document(raw_doc)


def _read_source_file(file_path: pathlib.Path,
                      file_path_for_error_message: pathlib.Path,
                      file_inclusion_chain: Sequence[SourceLocation]) -> ParseSource:
    try:
        return new_for_file(file_path)
    except OSError as ex:
        raise FileAccessError(file_path_for_error_message,
                              str(ex),
                              file_inclusion_chain)


def internal_conf_of(configuration: SectionsConfiguration) -> _SectionsConfigurationInternal:
    return _SectionsConfigurationInternal(configuration.sections(),
                                          configuration.default_section_name,
                                          configuration.section_element_name_for_error_messages)


RawDoc = Dict[str, List[SectionContentElement]]


def parse_file(conf: _SectionsConfigurationInternal,
               file_path: pathlib.Path,
               file_inclusion_chain: Sequence[line_source.SourceLocation],
               file_reference_relativity_root_dir: pathlib.Path,
               previously_visited_paths: List[pathlib.Path],
               ) -> RawDoc:
    path_to_file = file_reference_relativity_root_dir / file_path
    source = _read_source_file(path_to_file,
                               file_path,
                               file_inclusion_chain)
    resolved_path_of_current_file = path_to_file.resolve()
    if resolved_path_of_current_file in previously_visited_paths:
        raise FileAccessError(file_path,
                              'Cyclic inclusion of file',
                              file_inclusion_chain)
    visited_paths = previously_visited_paths + [resolved_path_of_current_file]
    file_reference_relativity_root_dir = path_to_file.parent
    return _parse_source(conf,
                         SectionContentElementBuilder(file_path,
                                                      file_inclusion_chain,
                                                      resolved_path_of_current_file.parent),
                         file_reference_relativity_root_dir,
                         source,
                         visited_paths)


def parse_source(conf: _SectionsConfigurationInternal,
                 element_builder: SectionContentElementBuilder,
                 file_reference_relativity_root_dir: pathlib.Path,
                 source: ParseSource,
                 ) -> model.Document:
    raw_doc = _parse_source(conf,
                            element_builder,
                            file_reference_relativity_root_dir,
                            source,
                            [])
    return build_document(raw_doc)


def _parse_source(conf: _SectionsConfigurationInternal,
                  element_builder: SectionContentElementBuilder,
                  file_reference_relativity_root_dir: pathlib.Path,
                  source: ParseSource,
                  visited_paths: List[pathlib.Path],
                  ) -> RawDoc:
    impl = _Impl(conf,
                 element_builder,
                 file_reference_relativity_root_dir,
                 source,
                 visited_paths)
    return impl.apply()


def _add_raw_doc(added_to: RawDoc,
                 to_add: RawDoc):
    for key, elements in to_add.items():
        if key in added_to:
            added_to[key].extend(elements)
        else:
            added_to[key] = elements


class _SectionContentsElementConstructor(ParsedSectionElementVisitor):
    def __init__(self, element_builder: SectionContentElementBuilder):
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
                                       ) -> ParsedFileInclusionDirective:
        return file_inclusion


class _Impl:
    def __init__(self,
                 configuration: _SectionsConfigurationInternal,
                 element_builder: SectionContentElementBuilder,
                 file_reference_relativity_root_dir: pathlib.Path,
                 document_source: ParseSource,
                 visited_paths: List[pathlib.Path]):
        self.configuration = configuration
        self._element_builder = element_builder
        # self._file_reference_relativity_root_dir = file_reference_relativity_root_dir
        self._fs_location_info = FileSystemLocationInfo(file_reference_relativity_root_dir)
        self._document_source = document_source
        self._current_line = self._get_current_line_or_none_if_is_at_eof()
        self._parser_for_current_section = None
        self._name_of_current_section = None
        self._elements_for_current_section = []
        self._section_name_2_element_list = {}
        self._element_constructor = _SectionContentsElementConstructor(element_builder)
        self.visited_paths = visited_paths

    @property
    def parser_for_current_section(self) -> SectionElementParser:
        return self._parser_for_current_section

    def apply(self) -> RawDoc:
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
                        raise FileSourceError(new_source_error_of_single_line(self._current_line,
                                                                              msg),
                                              None,
                                              self._location_path_of_current_line())
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
                raise FileSourceError(new_source_error_of_single_line(section_line,
                                                                      msg),
                                      None,
                                      self._location_path_of_current_line())
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
                parsed_element = self.parse_element_at_current_line_using_current_section_element_parser()
            except SourceError as ex:
                raise FileSourceError(ex, self._name_of_current_section,
                                      self._element_builder.location_path_of(ex.source))
            if isinstance(parsed_element, model.SectionContentElement):
                self.add_element_to_current_section(parsed_element)
            else:
                assert isinstance(parsed_element, ParsedFileInclusionDirective)
                self._include_files(parsed_element)

            self._current_line = self._get_current_line_or_none_if_is_at_eof()

    def parse_element_at_current_line_using_current_section_element_parser(self):
        parsed_element = self.parser_for_current_section.parse(self._fs_location_info,
                                                               self._document_source)
        if parsed_element is None:
            raise FileSourceError(new_source_error_of_single_line(self._document_source.current_line,
                                                                  'Syntax error'),
                                  self._name_of_current_section,
                                  self._location_path_of_current_line())
        return self._element_constructor.visit(parsed_element)

    def add_element_to_current_section(self, element: model.SectionContentElement):
        self._elements_for_current_section.append(element)

    def extract_section_name_and_consume_line(self) -> str:
        try:
            section_name = syntax.extract_section_name_from_section_line(self._current_line.text)
        except ValueError as ex:
            raise FileSourceError(new_source_error_of_single_line(self._current_line,
                                                                  str(ex)),
                                  None,
                                  self._location_path_of_current_line())
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

    def _location_path_of_current_line(self) -> Sequence[line_source.SourceLocation]:
        source = line_source.single_line_sequence(self._document_source.current_line_number,
                                                  self._document_source.current_line_text)
        return self._element_builder.location_path_of(source)

    def current_line_is_comment_or_empty(self):
        return syntax.EMPTY_LINE_RE.match(self._current_line.text) or \
               syntax.COMMENT_LINE_RE.match(self._current_line.text)

    def _include_files(self, inclusion_directive: ParsedFileInclusionDirective):
        conf = _SectionsConfigurationInternal(self.configuration.section2parser,
                                              self._name_of_current_section,
                                              self.configuration.section_element_name_for_error_messages)
        for file_to_include in inclusion_directive.files_to_include:
            included_doc = parse_file(conf,
                                      file_to_include,
                                      self._element_builder.location_path_of(inclusion_directive.source),
                                      self._fs_location_info.file_reference_relativity_root_dir,
                                      self.visited_paths)
            _add_raw_doc(self._section_name_2_element_list, included_doc)


def resolve_file_reference_relativity_root_dir(relativity_root: pathlib.Path,
                                               file_inclusion_chain: Sequence[line_source.SourceLocation]
                                               ) -> pathlib.Path:
    try:
        return relativity_root.resolve()
    except RuntimeError as ex:
        raise FileAccessError(relativity_root,
                              str(ex),
                              file_inclusion_chain)


def build_document(raw_doc: RawDoc) -> model.Document:
    return model.Document({
        section_name: model.SectionContents(tuple(elements))
        for section_name, elements in raw_doc.items()
    })