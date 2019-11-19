from exactly_lib.common.report_rendering import text_docs
from exactly_lib.definitions.test_case.instructions import define_symbol
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.program.command.driver_sdvs import CommandDriverSdvForSystemProgram
from exactly_lib.test_case_utils.program.parse import parse_arguments
from exactly_lib.test_case_utils.program.sdvs import accumulator
from exactly_lib.test_case_utils.program.sdvs.command_program_sdv import ProgramSdvForCommand
from exactly_lib.type_system.value_type import DataValueType
from exactly_lib.util import strings


def parse_as_command(parser: TokenParser) -> CommandSdv:
    program_name = parse_string.parse_string_from_token_parser(parser, _PARSE_NAME_CONF)
    additional_arguments = parse_arguments.parse_from_token_parser(parser)

    return CommandSdv(CommandDriverSdvForSystemProgram(program_name),
                      additional_arguments)


def parse_as_program(parser: TokenParser) -> ProgramSdv:
    command_sdv = parse_as_command(parser)
    return ProgramSdvForCommand(command_sdv, accumulator.empty())


def command_parser() -> Parser[CommandSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_as_command)


def program_parser() -> Parser[ProgramSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_as_program)


_PROGRAM_NAME_STRING_REFERENCES_RESTRICTION = string_made_up_by_just_strings(
    text_docs.single_pre_formatted_line_object(
        strings.FormatMap(
            'A program name must be defined in terms of {string_type}.',
            {'string_type': define_symbol.DATA_TYPE_INFO_DICT[DataValueType.STRING].identifier},
        )
    )
)

_PARSE_NAME_CONF = parse_string.Configuration('NAME',
                                              _PROGRAM_NAME_STRING_REFERENCES_RESTRICTION)
