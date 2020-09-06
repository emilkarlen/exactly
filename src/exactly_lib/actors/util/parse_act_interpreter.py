from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import rel_opts_configuration, path_relativities
from exactly_lib.test_case_utils.parse.shell_syntax import SHELL_KEYWORD
from exactly_lib.test_case_utils.program import syntax_elements as program_syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_executable_file, parse_system_program

SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD = SHELL_KEYWORD
_MISSING_INTERPRETER_MSG = 'Missing ' + syntax_elements.ACT_INTERPRETER_SYNTAX_ELEMENT.singular_name


def parser() -> Parser[CommandSdv]:
    return _Parser()


class _Parser(ParserFromTokenParserBase[CommandSdv]):
    def __init__(self):
        super().__init__(False, False)
        self._parser_of_executable_file = parse_executable_file.parser_of_command(EXE_FILE_RELATIVITIES)
        self._command_variant_setups = {
            program_syntax_elements.SYSTEM_PROGRAM_TOKEN:
                parse_system_program.command_parser().parse_from_token_parser,
        }

    def parse_from_token_parser(self, token_parser: TokenParser) -> CommandSdv:
        return token_parser.parse_default_or_optional_command(
            self._parser_of_executable_file.parse_from_token_parser,
            self._command_variant_setups,
            False,
        )


EXE_FILE_RELATIVITIES = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        path_relativities.HDS_AND_ABS_RELATIVITY_VARIANTS,
        RelOptionType.REL_HDS_CASE,
    ),
    instruction_arguments.PATH_SYNTAX_ELEMENT_NAME,
    True,
)