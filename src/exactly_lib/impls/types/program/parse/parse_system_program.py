from exactly_lib.common.report_rendering import text_docs
from exactly_lib.definitions.test_case.instructions import define_symbol
from exactly_lib.impls.types.program.command.driver_sdvs import CommandDriverSdvForSystemProgram
from exactly_lib.impls.types.program.parse import parse_arguments
from exactly_lib.impls.types.program.sdvs.command_program_sdv import ProgramSdvForCommand
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import Parser, ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.value_type import WithStrRenderingType
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    is_string__all_indirect_refs_are_strings
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.util.str_ import str_constructor


def parse_as_command(token_parser: TokenParser) -> CommandSdv:
    parser = command_parser()
    return parser.parse_from_token_parser(token_parser)


def parse_as_program(token_parser: TokenParser) -> ProgramSdv:
    parser = program_parser()
    return parser.parse_from_token_parser(token_parser)


def command_parser() -> Parser[CommandSdv]:
    return _ParseAsCommand()


def program_parser() -> Parser[ProgramSdv]:
    return _ParseAsProgram()


class _ParseAsProgram(ParserFromTokenParserBase[ProgramSdv]):
    def __init__(self):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=False)
        self._command_parser = _ParseAsCommand()

    def parse_from_token_parser(self, parser: TokenParser) -> ProgramSdv:
        return ProgramSdvForCommand(
            self._command_parser.parse_from_token_parser(parser),
            AccumulatedComponents.empty(),
        )


class _ParseAsCommand(ParserFromTokenParserBase[CommandSdv]):
    def __init__(self):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=False)
        self._arguments_parser = parse_arguments.parser()

    def parse_from_token_parser(self, parser: TokenParser) -> CommandSdv:
        program_name = parse_string.parse_string_from_token_parser(parser, _PARSE_NAME_CONF)
        arguments = self._arguments_parser.parse_from_token_parser(parser)
        return CommandSdv(CommandDriverSdvForSystemProgram(program_name),
                          arguments)


_PROGRAM_NAME_STRING_REFERENCES_RESTRICTION = is_string__all_indirect_refs_are_strings(
    text_docs.single_pre_formatted_line_object(
        str_constructor.FormatMap(
            'A program name must be defined in terms of {string_type}.',
            {'string_type': define_symbol.TYPE_W_STR_RENDERING_INFO_DICT[WithStrRenderingType.STRING].identifier},
        )
    )
)

_PARSE_NAME_CONF = parse_string.Configuration('NAME',
                                              _PROGRAM_NAME_STRING_REFERENCES_RESTRICTION)
