from shelltest.document import model
from shelltest.general import line_source
from shelltest.general.line_source import LineSource
from shelltest.document import syntax


class SourceError(Exception):
    """
    An exceptions related to a line in the test case.
    """

    def __init__(self,
                 line: line_source.Line,
                 message: str):
        self._line = line
        self._message = message


class PlainTestCaseParser:
    """
    Base class for parsers that parse a "plain test case"
    (i.e., a test case that do not need pre-processing).
    """

    def apply(self,
              plain_test_case: LineSource) -> model.Document:
        """
        :raises SourceError The test case cannot be parsed.
        """
        raise NotImplementedError()


class InstructionForComment(model.PhaseContentElement):
    def __init__(self, source_line: line_source.Line):
        model.PhaseContentElement.__init__(self, source_line)

    def execute(self, phase_name: str, global_environment, phase_environment):
        pass


class InstructionParser:
    """
    Parses an instruction line into an instruction.
    """

    def apply(self, source_line: line_source.Line) -> model.PhaseContentElement:
        """
        :raises SourceError The instruction line cannot be parsed.
        """
        raise NotImplementedError()


class ParserForPhase(tuple):
    def __new__(cls,
                phase: str,
                parser: InstructionParser):
        return tuple.__new__(cls, (phase, parser))

    @property
    def phase(self) -> str:
        return self[0]

    @property
    def parser(self) -> InstructionParser:
        return self[1]


class PhaseAndInstructionsConfiguration:
    """
    Phases and their instruction parser.
    """

    def __init__(self,
                 parser_for_anonymous_phase: InstructionParser,
                 parsers_for_named_phases: tuple):
        """
        :param parser_for_anonymous_phase: Parser for the top-level/anonymous phase. None if that phase
         is not used.
        :param parsers_for_named_phases: sequence of ParserForPhase.
        """
        self._parser_for_anonymous_phase = parser_for_anonymous_phase
        self._parsers_for_named_phases = parsers_for_named_phases
        phase_names_in_order_of_execution = []
        phase2parser = {}
        if parser_for_anonymous_phase:
            phase_names_in_order_of_execution.append(None)
            phase2parser[None] = parser_for_anonymous_phase
        for pfp in parsers_for_named_phases:
            phase_names_in_order_of_execution.append(pfp.phase)
            phase2parser[pfp.phase] = pfp.parser
        self._phase_names_in_order_of_execution = tuple(phase_names_in_order_of_execution)
        self._phase2parser = phase2parser

    def phase_names_in_order_of_execution(self) -> tuple:
        """
        Sequence of all Phase Names, in the order of execution (same order as given to constructor.
        The Phase Name None represents the anonymous Phase.
        :return: tuple of str:s
        """
        return self._phase_names_in_order_of_execution

    def parser_for_phase(self, phase_name: str) -> InstructionParser:
        """
        :param phase_name None denotes the anonymous phase.
        """
        return self._phase2parser[phase_name]


def skip_empty_and_classify_lines(plain_test_case: line_source.LineSource) -> list:
    """
    :param plain_test_case:
    :return: List of (syntax.TYPE_-constant, Line)
    """
    ret_val = []
    for line in plain_test_case:
        type_const = syntax.classify_line(line.text)
        if type_const != syntax.TYPE_EMPTY:
            ret_val.append((type_const, line))
    return ret_val


class PhaseWithLines(tuple):
    def __new__(cls,
                phase_name: str,
                phase_source_line: line_source.Line,
                lines_in_phase: tuple):
        return tuple.__new__(cls, (phase_name, phase_source_line, lines_in_phase))

    @property
    def phase_name(self) -> str:
        return self[0]

    @property
    def phase_source_line(self) -> line_source.Line:
        return self[1]

    @property
    def lines_in_phase(self) -> tuple:
        return self[2]


def group_by_phase(classified_nonempty_lines: list) -> list:
    """
    Parses phases and groups the instruction and comment lines by
    :param classified_nonempty_lines: List of (syntax.TYPE_-constant, line_source.Line), with no
    lines having type syntax.TYPE_EMPTY.
    :raise model.SourceError Encountered an invalid phase header.
    :return: List of PhaseWithLines.
    """
    ret_val = []
    phase_name = None
    phase_line = None
    phase_with_lines = _extract_and_remove_phase(phase_name, phase_line, classified_nonempty_lines)
    if phase_with_lines.lines_in_phase:
        ret_val.append(phase_with_lines)
    while classified_nonempty_lines:
        phase_type_const, phase_line = classified_nonempty_lines[0]
        del classified_nonempty_lines[0]
        try:
            phase_name = syntax.extract_phase_name_from_phase_line(phase_line.text)
        except syntax.GeneralError:
            raise SourceError(phase_line,
                              'Invalid syntax of phase (should have syntax %s)' % syntax.PHASE_SYNTAX)
        phase_with_lines = _extract_and_remove_phase(phase_name, phase_line, classified_nonempty_lines)
        ret_val.append(phase_with_lines)
    return ret_val


def _extract_and_remove_phase(phase_name: str,
                              phase_line: line_source.Line,
                              classified_nonempty_lines: list) -> PhaseWithLines:
    """
    Extracts all instructions until next phase, and removes these instructions from the input.
    :param phase_name: Name of the current group (already parsed)
    :param classified_nonempty_lines: list of (syntax.TYPE_-const, line_source.Line).
    First line is first "content-line" of the phase to extract (which can be a phase-header, in which
    case the phase to extract is empty).
    """
    instructions_list = []
    while classified_nonempty_lines:
        type_const, line = classified_nonempty_lines[0]
        if type_const == syntax.TYPE_PHASE:
            return PhaseWithLines(phase_name, phase_line, tuple(instructions_list))
        instructions_list.append(classified_nonempty_lines[0])
        del classified_nonempty_lines[0]
    return PhaseWithLines(phase_name, phase_line, tuple(instructions_list))


def accumulate_identical_phases(phase_with_lines_list: list) -> dict:
    """
    Accumulates the lines for repeated phases.
    The order of the lines for each phase is preserved, so that a line later in the file succeeds a line
    earlier in the file.
    :param phase_with_lines_list: list of PhaseWithLines
    :return: dict: phase-name -> [line_source.Line]
    """
    ret_val = {}
    for phase_with_lines in phase_with_lines_list:
        if phase_with_lines.lines_in_phase:
            if phase_with_lines.phase_name not in ret_val:
                ret_val[phase_with_lines.phase_name] = []
            ret_val[phase_with_lines.phase_name].extend(phase_with_lines.lines_in_phase)
    return ret_val


class _PlainTestCaseParserForPhaseAndInstructionsConfiguration(PlainTestCaseParser):
    def __init__(self, configuration: PhaseAndInstructionsConfiguration):
        self._configuration = configuration

    def apply(self, plain_test_case: line_source.LineSource) -> model.Document:
        classified_nonempty_lines = skip_empty_and_classify_lines(plain_test_case)
        instructions_and_comments_grouped_by_phase = group_by_phase(classified_nonempty_lines)
        self._raise_exception_if_there_is_an_invalid_phase_name(instructions_and_comments_grouped_by_phase)
        phase2lines = accumulate_identical_phases(instructions_and_comments_grouped_by_phase)
        return self.parse_instruction_lines(phase2lines)

    def _raise_exception_if_there_is_an_invalid_phase_name(self, instructions_and_comments_grouped_by_phase):
        phase_names_in_configuration = self._configuration.phase_names_in_order_of_execution()
        for phase_with_instructions in instructions_and_comments_grouped_by_phase:
            if phase_with_instructions.phase_name not in phase_names_in_configuration:
                raise SourceError(phase_with_instructions.phase_source_line,
                                  'Unknown phase: %s (valid phases are %s)' %
                                  (phase_with_instructions.phase_name,
                                   self._valid_phases_presentation_list(phase_names_in_configuration)))

    @staticmethod
    def _valid_phases_presentation_list(internal_phase_names: tuple):
        def quote(name):
            return "'" + name + "'"

        names = map(lambda phase_name: quote(phase_name) if phase_name else syntax.ANONYMOUS_PHASE_PRESENTATION_NAME,
                    internal_phase_names)
        return ', '.join(names)

    def parse_instruction_lines(self, phase2c_lines: dict) -> model.Document:
        """
        :param phase2c_lines: dict: str -> iterable of (syntax.TYPE_-constant, line_source.Line)
        """
        phase2instruction_sequence = {}
        for phase_name in self._configuration.phase_names_in_order_of_execution():
            if phase_name in phase2c_lines:
                phase2instruction_sequence[phase_name] = \
                    self.parse_instruction_lines_for_phase(phase_name,
                                                           phase2c_lines[phase_name])
        return model.Document(phase2instruction_sequence)

    def parse_instruction_lines_for_phase(self, phase_name: str, c_lines: tuple) -> model.PhaseContents:
        parser = self._configuration.parser_for_phase(phase_name)
        sequence = []
        for line_type, line in c_lines:
            if line_type == syntax.TYPE_COMMENT:
                sequence.append(model.new_comment_element(line))
            else:
                sequence.append(parser.apply(line))
        return model.PhaseContents(tuple(sequence))


def new_parser_for(configuration: PhaseAndInstructionsConfiguration) -> PlainTestCaseParser:
    return _PlainTestCaseParserForPhaseAndInstructionsConfiguration(configuration)
