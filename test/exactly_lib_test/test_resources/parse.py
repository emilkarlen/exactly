import shlex

from exactly_lib.section_document import parse
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib.util import line_source
from exactly_lib.util.line_source import LineSequenceBuilder


def new_source(instruction_name: str, arguments: str) -> SingleInstructionParserSource:
    first_line = instruction_name + ' ' + arguments
    return SingleInstructionParserSource(
        new_line_sequence(first_line),
        arguments)


def new_source2(first_line_arguments: str,
                following_lines: list = ()) -> SingleInstructionParserSource:
    first_line = 'instruction-name' + ' ' + first_line_arguments
    return SingleInstructionParserSource(
        new_line_sequence(first_line, tuple(following_lines)),
        first_line_arguments)


def source3(lines: list) -> ParseSource:
    return ParseSource('\n'.join(lines))


def source4(first_line: str,
            following_lines: list = ()) -> ParseSource:
    return ParseSource('\n'.join([first_line] + list(following_lines)))


def single_line_source(arguments: str) -> SingleInstructionParserSource:
    first_line = 'instruction-name' + ' ' + arguments
    return SingleInstructionParserSource(
        new_line_sequence(first_line),
        arguments)


def single_line_sourcE(arguments: str) -> ParseSource:
    remaining_part_of_current_line = arguments
    return source4(remaining_part_of_current_line)


def multi_line_source(first_line_arguments: str,
                      following_lines: list) -> SingleInstructionParserSource:
    first_line = 'instruction-name' + ' ' + first_line_arguments
    return SingleInstructionParserSource(
        new_line_sequence(first_line,
                          following_lines=tuple(following_lines)),
        first_line_arguments)


def argument_list_source(arguments: list,
                         following_lines: iter = ()) -> SingleInstructionParserSource:
    return multi_line_source(' '.join(map(shlex.quote, arguments)),
                             following_lines)


def new_line_sequence(first_line: str,
                      following_lines: tuple = ()) -> LineSequenceBuilder:
    return line_source.LineSequenceBuilder(
        parse.LineSequenceSourceFromListOfLines(
            parse.ListOfLines(list(following_lines))),
        1,
        first_line)
