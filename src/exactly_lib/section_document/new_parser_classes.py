from exactly_lib.section_document import model
from exactly_lib.section_document import syntax
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parse import SectionsConfiguration, SourceError, FileSourceError

from exactly_lib.util import line_source


class ElementParser2:
    def parse(self, source: ParseSource) -> model.SectionContentElement:
        raise NotImplementedError()


class PlainDocumentParser2:
    """
    Base class for parsers that parse a "plain file"
    (i.e., a file that do not need pre-processing).
    """

    def parse(self, source: ParseSource) -> model.Document:
        """
        :raises FileSourceError The test case cannot be parsed.
        """
        raise NotImplementedError()


class SectionElementParser2:
    def parse(self, source: ParseSource) -> model.SectionContentElement:
        """
        :raises FileSourceError The element cannot be parsed.
        """
        raise NotImplementedError()


class InstructionParser2:
    def parse(self, source: ParseSource) -> model.Instruction:
        """
        :raises FileSourceError The instruction cannot be parsed.
        """
        raise NotImplementedError()


def new_parser_for(configuration: SectionsConfiguration) -> PlainDocumentParser2:
    return _PlainDocumentParserForSectionsConfiguration2(configuration)


class _PlainDocumentParserForSectionsConfiguration2(PlainDocumentParser2):
    def __init__(self, configuration: SectionsConfiguration):
        self._configuration = configuration

    def parse(self, source: ParseSource) -> model.Document:
        return _Impl(self._configuration, source).apply()


# class _ParseImpl:
#     def __init__(self, configuration: SectionsConfiguration, source: ParseSource):
#         self.configuration = configuration
#         self.doc_parser = doc_parser
#         self.source = source
#         self.result = {}
#         self.current_senction_name = doc_parser.default_section_name
#         self.current_section_element_parser = doc_parser.section_name_2_element_parser[doc_parser.default_section_name]
# 
#     def parse(self):
#         while not self.source.is_at_eof():
#             self.parse_one_thing()
# 
#     def parse_one_thing(self):
#         current_line = self.source.current_line
#         section_name = _section_name_if_section_line(current_line)
#         if section_name:
#             pass  # set current section and current element parser according to section
#             self.source.consume_current_line()
#         else:
#             element = self.current_section_element_parser.parse(self.source)
#             if not self.current_senction_name in self.result:
#                 self.result[self.current_senction_name] = []
#             self.result[self.current_senction_name].append(element)



class StdElementParser(ElementParser2):
    """
    A parser that knows how to parse empty lines and
    comment lines (denoted by standard syntax).
    Every other line is treated as the start of an
    instruction to be parsed by a given instruction parser.
    """

    def __init__(self, instruction_parser: InstructionParser2):
        self.instruction_parser = instruction_parser

    def parse(self, source: ParseSource) -> model.SectionContentElement:
        if self._is_empty_line(source.current_line):
            return model.SectionContentElement()  # empty
        if self._is_comment_line(source.current_line):
            return model.SectionContentElement()  # comment
        else:
            instruction = self.instruction_parser.parse(source)
            return model.SectionContentElement()  # instruction

    @staticmethod
    def _is_empty_line(current_line):
        raise NotImplementedError()

    @staticmethod
    def _is_comment_line(current_line):
        raise NotImplementedError()

    def _parse_description(self, source) -> str:
        raise NotImplementedError()

    def _consume_ignored_lines_and_space(self, source):
        raise NotImplementedError()


class _Impl:
    def __init__(self,
                 configuration: SectionsConfiguration,
                 document_source: ParseSource):
        self.configuration = configuration
        self._document_source = document_source
        # self._list_of_lines = ListOfLines(map(lambda l: l.text,
        #                                       self._document_source))
        self._current_line = self._get_current_line_or_none_if_is_at_eof()
        self._parser_for_current_section = None
        self._name_of_current_section = None
        self._elements_for_current_section = []
        self._section_name_2_element_list = {}

    @property
    def parser_for_current_section(self) -> SectionElementParser2:
        return self._parser_for_current_section

    # @property
    # def list_of_lines(self) -> ListOfLines:
    #     return self._list_of_lines

    def apply(self) -> model.Document:
        if self.is_at_eof():
            return model.empty_document()
        if self.current_line_is_section_line():
            self.switch_section_according_to_last_section_line_and_consume_section_lines()
            self.read_rest_of_document_from_inside_section_or_at_eof()
        else:
            if self.configuration.default_section_name is not None:
                self.set_current_section(self.configuration.default_section_name[0])
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
        return self.build_document()

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

            # self.forward_line_source_according_lines_consumed_by(element)
            self._current_line = self._get_current_line_or_none_if_is_at_eof()

    def parse_element_at_current_line_using_current_section_element_parser(self) -> model.SectionContentElement:
        # sequence_source = LineSequenceSourceFromListOfLines(self._list_of_lines.copy())
        # line_sequence_builder = line_source.LineSequenceBuilder(sequence_source,
        #                                                         self._current_line.line_number,
        #                                                         self._current_line.text)
        return self.parser_for_current_section.parse(self._document_source)

    def add_element_to_current_section(self, element: model.SectionContentElement):
        self._elements_for_current_section.append(element)

    # def forward_line_source_according_lines_consumed_by(self, element: model.SectionContentElement):
    #     self.list_of_lines.forward(len(element.source.lines) - 1)
    #     self.move_one_line_forward()

    def extract_section_name_and_consume_line(self) -> str:
        section_name = syntax.extract_section_name_from_section_line(self._current_line.text)
        self.move_one_line_forward()
        return section_name

    def build_document(self) -> model.Document:
        sections = {}
        for section_name, elements in self._section_name_2_element_list.items():
            sections[section_name] = model.SectionContents(tuple(elements))
        return model.Document(sections)

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
