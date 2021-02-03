from typing import Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import program
from exactly_lib.impls.types.parse.options import OptionalOptionWMandatoryArgumentParser
from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.impls.types.program import syntax_elements as pgm_syntax_elements
from exactly_lib.impls.types.program.parse import parse_executable_file, parse_system_program, \
    parse_shell_command, parse_with_reference_to_program
from exactly_lib.section_document.element_parsers.ps_or_tp import parser_opt_parens
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import Parser, ParserFromTokenParserBase, \
    CurrentLineMustNotBeEmptyExceptForSpace
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv


def program_parser(must_be_on_current_line: bool = False,
                   exe_file_relativity: RelOptionArgumentConfiguration
                   = pgm_syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF,
                   ) -> Parser[ProgramSdv]:
    parser_for_element_on_arbitrary_line = parser_opt_parens.OptionallySurroundedByParenthesesParser(
        _Parser(exe_file_relativity)
    )
    return (
        CurrentLineMustNotBeEmptyExceptForSpace.of_mandatory_element(
            syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
            parser_for_element_on_arbitrary_line,
        )
        if must_be_on_current_line
        else
        parser_for_element_on_arbitrary_line
    )


class _Parser(ParserFromTokenParserBase[ProgramSdv]):
    def __init__(self, exe_file_relativity: RelOptionArgumentConfiguration):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=False)
        self._string_transformer_parser = None
        self._string_source_parser = None
        self._parser_of_executable_file = parse_executable_file.parser_of_program(exe_file_relativity)
        self._program_variant_setups = {
            pgm_syntax_elements.SHELL_COMMAND_TOKEN:
                parse_shell_command.program_parser().parse_from_token_parser,

            pgm_syntax_elements.SYSTEM_PROGRAM_TOKEN:
                parse_system_program.program_parser().parse_from_token_parser,

            pgm_syntax_elements.SYMBOL_REF_PROGRAM_TOKEN:
                parse_with_reference_to_program.program_parser().parse_from_token_parser,
        }

    def parse_from_token_parser(self, parser: TokenParser) -> ProgramSdv:
        command_as_program = self._parse_command_and_arguments(parser)

        accumulated_components = AccumulatedComponents.empty()
        accumulated_components = accumulated_components.new_accumulated(self._parse_stdin(parser))
        accumulated_components = accumulated_components.new_accumulated(self._parse_transformation(parser))

        return command_as_program.new_accumulated(accumulated_components)

    def _parse_stdin(self, parser: TokenParser) -> AccumulatedComponents:
        optional_string_source = self._get_string_source_parser().parse_from_token_parser(parser)
        return (
            AccumulatedComponents.empty()
            if optional_string_source is None
            else
            AccumulatedComponents.of_stdin((optional_string_source,))
        )

    def _parse_transformation(self, parser: TokenParser) -> AccumulatedComponents:
        optional_transformer = self._get_string_transformer_parser().parse_from_token_parser(parser)
        return (
            AccumulatedComponents.empty()
            if optional_transformer is None
            else
            AccumulatedComponents.of_transformation(optional_transformer)
        )

    def _get_string_transformer_parser(self) -> Parser[Optional[StringTransformerSdv]]:
        if self._string_transformer_parser is None:
            from exactly_lib.impls.types.string_transformer import parse_transformation_option
            self._string_transformer_parser = parse_transformation_option.parser()

        return self._string_transformer_parser

    def _get_string_source_parser(self) -> Parser[Optional[StringSourceSdv]]:
        if self._string_source_parser is None:
            from exactly_lib.impls.types.string_source.parse import default_parser_for
            self._string_source_parser = OptionalOptionWMandatoryArgumentParser(
                program.STDIN_OPTION_NAME,
                default_parser_for(phase_is_after_act=False),
            )

        return self._string_source_parser

    def _parse_command_and_arguments(self, parser: TokenParser) -> ProgramSdv:
        return parser.parse_default_or_optional_command(
            self._parser_of_executable_file.parse_from_token_parser,
            self._program_variant_setups,
            False,
        )
