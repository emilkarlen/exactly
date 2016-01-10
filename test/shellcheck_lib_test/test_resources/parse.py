import shlex

from shellcheck_lib.document import parse
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.general import line_source
from shellcheck_lib.general.line_source import LineSequenceBuilder


def new_source(instruction_name: str, arguments: str) -> SingleInstructionParserSource:
    first_line = instruction_name + ' ' + arguments
    return SingleInstructionParserSource(
            new_line_sequence(first_line),
            arguments)


def new_source2(arguments: str) -> SingleInstructionParserSource:
    first_line = 'instruction name' + ' ' + arguments
    return SingleInstructionParserSource(
            new_line_sequence(first_line),
            arguments)


def single_line_source(arguments: str) -> SingleInstructionParserSource:
    first_line = 'instruction-name' + ' ' + arguments
    return SingleInstructionParserSource(
            new_line_sequence(first_line),
            arguments)


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
