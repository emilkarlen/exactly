from typing import Callable

from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.impls.types.program import syntax_elements
from exactly_lib.impls.types.program.parse import parse_executable_file, parse_system_program, \
    parse_shell_command, parse_with_reference_to_program
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import Parser, ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.util import functional


def program_parser(must_be_on_current_line: bool = False,
                   exe_file_relativity: RelOptionArgumentConfiguration = syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF,
                   ) -> Parser[ProgramSdv]:
    return _Parser(exe_file_relativity,
                   must_be_on_current_line=must_be_on_current_line)


class _Parser(ParserFromTokenParserBase[ProgramSdv]):
    def __init__(self,
                 exe_file_relativity: RelOptionArgumentConfiguration,
                 must_be_on_current_line: bool = False,
                 ):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=False)
        self._string_transformer_parser_fun = None
        self._must_be_on_current_line = must_be_on_current_line
        self._parser_of_executable_file = parse_executable_file.parser_of_program(exe_file_relativity)
        self._program_variant_setups = {
            syntax_elements.SHELL_COMMAND_TOKEN:
                parse_shell_command.program_parser().parse_from_token_parser,

            syntax_elements.SYSTEM_PROGRAM_TOKEN:
                parse_system_program.program_parser().parse_from_token_parser,

            syntax_elements.SYMBOL_REF_PROGRAM_TOKEN:
                parse_with_reference_to_program.program_parser().parse_from_token_parser,
        }

    def parse_from_token_parser(self, parser: TokenParser) -> ProgramSdv:
        command_as_program = self._parse_command_and_arguments(parser)

        optional_transformer = self._string_transformer_parser_function()(parser)

        def new_w_additional_transformer(transformer: StringTransformerSdv) -> ProgramSdv:
            return command_as_program.new_accumulated(AccumulatedComponents.of_transformation(transformer))

        return functional.reduce_optional(
            new_w_additional_transformer,
            command_as_program,
            optional_transformer,
        )

    def _string_transformer_parser_function(self) -> Callable[[TokenParser], StringTransformerSdv]:
        if self._string_transformer_parser_fun is None:
            from exactly_lib.impls.types.string_transformer import parse_transformation_option
            self._string_transformer_parser_fun = parse_transformation_option.parse_optional_option__optional

        return self._string_transformer_parser_fun

    def _parse_command_and_arguments(self, parser: TokenParser) -> ProgramSdv:
        return parser.parse_default_or_optional_command(self._parser_of_executable_file.parse_from_token_parser,
                                                        self._program_variant_setups,
                                                        self._must_be_on_current_line)
