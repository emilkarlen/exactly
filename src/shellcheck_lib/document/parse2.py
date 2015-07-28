from shellcheck_lib.document import model
from shellcheck_lib.document import syntax
from shellcheck_lib.general import line_source
from shellcheck_lib.general.line_source import LineSource


class SourceError(Exception):
    """
    An exceptions related to a line in the test case.
    """

    def __init__(self,
                 line: line_source.Line,
                 message: str):
        self._line = line
        self._message = message

    @property
    def line(self) -> line_source.Line:
        return self._line

    @property
    def message(self) -> str:
        return self._message


class PlainDocumentParser:
    """
    Base class for parsers that parse a "plain file"
    (i.e., a file that do not need pre-processing).
    """

    def apply(self,
              plain_test_case: LineSource) -> model.Document:
        """
        :raises SourceError The test case cannot be parsed.
        """
        raise NotImplementedError()


class SectionElementParser:
    """
    Parses a single element in a section.
    """

    def apply(self, source: line_source.LineSequenceBuilder) -> model.PhaseContentElement:
        """
        :param source: The first line is not a section-header.

        :raises SourceError Syntax error.
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
    Phases and their instruction parser.
    """

    def __init__(self,
                 parser_for_anonymous_section: SectionElementParser,
                 parsers_for_named_sections: tuple):
        """
        :param parser_for_anonymous_section: Parser for the top-level/anonymous phase. None if that phase
         is not used.
        :param parsers_for_named_sections: sequence of SectionConfiguration.
        """
        self._parser_for_anonymous_section = parser_for_anonymous_section
        self._parsers_for_named_sections = parsers_for_named_sections
        section_names = []
        section2parser = {}
        if parser_for_anonymous_section:
            section_names.append(None)
            section2parser[None] = parser_for_anonymous_section
        for pfp in parsers_for_named_sections:
            section_names.append(pfp.section_name)
            section2parser[pfp.section_name] = pfp.parser
        self._section_list_as_tuple = tuple(section_names)
        self._section2parser = section2parser

    def section_names(self) -> tuple:
        """
        Sequence of all Phase Names (same order as given to constructor.
        The Phase Name None represents the anonymous Phase.
        :return: tuple of str:s
        """
        return self._section_list_as_tuple

    def parser_for_section(self, section_name: str) -> SectionElementParser:
        """
        :param section_name None denotes the anonymous section.
        """
        return self._section2parser[section_name]

    def has_section(self, section_name: str) -> bool:
        return section_name in self._section2parser


def new_parser_for(configuration: SectionsConfiguration) -> PlainDocumentParser:
    return _PlainDocumentParserForSectionsConfiguration(configuration)


class _PlainDocumentParserForSectionsConfiguration(PlainDocumentParser):
    def __init__(self, configuration: SectionsConfiguration):
        self._configuration = configuration

    def apply(self, plain_test_case: LineSource) -> model.Document:
        return _Impl(self._configuration,
                     plain_test_case).apply()


class ListOfLines:
    def __init__(self, lines: iter):
        self.next_line_number = 1
        self.lines = list(lines)

    def has_next(self) -> bool:
        return len(self.lines) > 0

    def next(self) -> line_source.Line:
        ret_val = line_source.Line(self.next_line_number,
                                   self.lines.pop(0))
        self.next_line_number += 1
        return ret_val

    def return_line(self, line: str):
        self.lines.insert(0, line)
        self.next_line_number -= 1

    def forward(self, number_of_lines: int):
        del self.lines[:number_of_lines]
        self.next_line_number += number_of_lines

    def copy(self):
        ret_val = ListOfLines(iter([]))
        ret_val.next_line_number = self.next_line_number
        ret_val.lines = self.lines.copy()
        return ret_val


class LineSequenceSourceFromListOfLines(line_source.LineSequenceSource):
    def __init__(self, list_of_lines: ListOfLines):
        self.list_of_lines = list_of_lines

    def has_next(self) -> bool:
        return self.list_of_lines.has_next()

    def next_line(self) -> str:
        return self.list_of_lines.next().text

    def return_line(self, line: str):
        self.list_of_lines.return_line(line)


class _Impl:
    def __init__(self,
                 configuration: SectionsConfiguration,
                 plain_test_case: LineSource):
        self.configuration = configuration
        self._plain_test_case = plain_test_case
        self._list_of_lines = ListOfLines(map(lambda l: l.text,
                                              self._plain_test_case))
        self._current_line = self._get_next_line()
        self._parser_for_current_section = None
        self._elements_for_current_section = []
        self._section_name_2_element_list = {}

    @property
    def parser_for_current_section(self) -> SectionElementParser:
        return self._parser_for_current_section

    @property
    def list_of_lines(self) -> ListOfLines:
        return self._list_of_lines

    def apply(self) -> model.Document:
        if self.is_at_eof():
            return model.empty_document()
        if self.current_line_is_section_line():
            self.switch_section_according_to_current_line_and_consume_section_lines()
            self.read_rest_of_document_from_inside_section_or_at_eof()
        else:
            if self.has_section(None):
                self.set_current_section(None)
                self.read_rest_of_document_from_inside_section_or_at_eof()
            else:
                self.skip_standard_comment_and_empty_lines()
                if not self.is_at_eof():
                    if self.current_line_is_section_line():
                        self.switch_section_according_to_current_line_and_consume_section_lines()
                        self.read_rest_of_document_from_inside_section_or_at_eof()
                    else:
                        raise SourceError(self._current_line,
                                          'Instruction outside of section')
        return self.build_document()

    def switch_section_according_to_current_line_and_consume_section_lines(self):
        """
        Precondition: Current line is a section-line
        Post condition: Current line is not a section-line.

        If there are many consecutive section lines, then all of these are consumed.
        """
        while not self.is_at_eof() and self.current_line_is_section_line():
            section_name = self.extract_section_name_and_consume_line()
            if not self.has_section(section_name):
                raise SourceError(self._current_line,
                                  'There is no section named ' + section_name)
            self.set_current_section(section_name)

    def read_rest_of_document_from_inside_section_or_at_eof(self):
        while True:
            if self.is_at_eof():
                return
            self.read_section_elements_until_next_section_or_eof()
            if self.is_at_eof():
                return
            if self.current_line_is_section_line():
                self.switch_section_according_to_current_line_and_consume_section_lines()

    def read_section_elements_until_next_section_or_eof(self):
        while not self.is_at_eof() and not self.current_line_is_section_line():
            element = self.parse_element_at_current_line_using_current_section_element_parser()
            self.add_element_to_current_section(element)
            self.forward_line_source_according_lines_consumed_by(element)

    def parse_element_at_current_line_using_current_section_element_parser(self) -> model.PhaseContentElement:
        sequence_source = LineSequenceSourceFromListOfLines(self._list_of_lines.copy())
        line_sequence_builder = line_source.LineSequenceBuilder(sequence_source,
                                                                self._current_line.line_number,
                                                                self._current_line.text)
        return self._parser_for_current_section.apply(line_sequence_builder)

    def add_element_to_current_section(self, element: model.PhaseContentElement):
        self._elements_for_current_section.append(element)

    def forward_line_source_according_lines_consumed_by(self, element: model.PhaseContentElement):
        self.list_of_lines.forward(len(element.source.lines) - 1)
        self.next_line()

    def extract_section_name_and_consume_line(self) -> str:
        section_name = syntax.extract_phase_name_from_phase_line(self._current_line.text)
        self.next_line()
        return section_name

    def build_document(self) -> model.Document:
        sections = {}
        for section_name, elements in self._section_name_2_element_list.items():
            sections[section_name] = model.PhaseContents(tuple(elements))
        return model.Document(sections)

    def set_current_section(self, section_name: str):
        self._parser_for_current_section = self.configuration.parser_for_section(section_name)
        if section_name not in self._section_name_2_element_list:
            self._section_name_2_element_list[section_name] = []
        self._elements_for_current_section = self._section_name_2_element_list[section_name]

    def has_section(self, section_name: str) -> bool:
        return self.configuration.has_section(section_name)

    def next_line(self):
        self._current_line = self._get_next_line()

    def is_at_eof(self) -> bool:
        return self._current_line is None

    def current_line_is_section_line(self) -> bool:
        return syntax.PHASE_LINE_RE.match(self._current_line.text)

        # @property
        # def configuration(self) -> SectionsConfiguration:
        #     raise NotImplementedError()

    def skip_standard_comment_and_empty_lines(self):
        while not self.is_at_eof():
            if not self.current_line_is_comment_or_empty():
                break
            self.next_line()

    def _get_next_line(self) -> line_source.Line:
        return None \
            if not self._list_of_lines.has_next() \
            else self._list_of_lines.next()

    def current_line_is_comment_or_empty(self):
        return syntax.EMPTY_LINE_RE.match(self._current_line.text) or \
               syntax.COMMENT_LINE_RE.match(self._current_line.text)
