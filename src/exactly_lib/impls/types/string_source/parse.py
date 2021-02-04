from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.path import parse_path
from exactly_lib.impls.types.program.parse import parse_program
from exactly_lib.impls.types.string_ import parse_here_document
from exactly_lib.impls.types.string_.parse_string import parse_string_from_token_parser
from exactly_lib.impls.types.string_source import sdvs
from exactly_lib.impls.types.string_transformer import parse_transformation_option
from exactly_lib.section_document.element_parsers import token_stream_parsing
from exactly_lib.section_document.element_parsers.ps_or_tp import parser_opt_parens
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.util.parse import token_matchers
from exactly_lib.util.parse.token import Token
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from . import defs
from ..path.rel_opts_configuration import RelOptionsConfiguration, RelOptionArgumentConfiguration


def default_parser_for(phase_is_after_act: bool,
                       default_relativity: RelOptionType = RelOptionType.REL_HDS_CASE,
                       ) -> Parser[StringSourceSdv]:
    return string_source_parser(
        defs.src_rel_opt_arg_conf_for_phase(phase_is_after_act, default_relativity).options
    )


def string_source_parser(accepted_file_relativities: RelOptionsConfiguration) -> Parser[StringSourceSdv]:
    return parser_opt_parens.OptionallySurroundedByParenthesesParser(
        _StringSourceParserWoParens(accepted_file_relativities)
    )


class _StringSourceParserWoParens(ParserFromTokenParserBase[StringSourceSdv]):
    def __init__(self, accepted_file_relativities: RelOptionsConfiguration):
        super().__init__(False, False)
        self._variants_parser = token_stream_parsing.ParserOfMandatoryChoiceWithDefault2(
            syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT.singular_name,
            [
                token_stream_parsing.TokenSyntaxSetup2(
                    token_matchers.is_option(defs.FILE_OPTION),
                    _FileParser(accepted_file_relativities).parse,
                ),
                token_stream_parsing.TokenSyntaxSetup2(
                    token_matchers.is_option(defs.PROGRAM_OUTPUT_OPTIONS[ProcOutputFile.STDOUT]),
                    _ProgramOutputParser(ProcOutputFile.STDOUT).parse,
                ),
                token_stream_parsing.TokenSyntaxSetup2(
                    token_matchers.is_option(defs.PROGRAM_OUTPUT_OPTIONS[ProcOutputFile.STDERR]),
                    _ProgramOutputParser(ProcOutputFile.STDERR).parse,
                ),
                token_stream_parsing.TokenSyntaxSetup2(
                    parse_here_document.HereDocArgTokenMatcher(),
                    _parse_here_doc,
                ),
            ],
            _parse_string,
        )

    def parse_from_token_parser(self, parser: TokenParser) -> StringSourceSdv:
        return self._variants_parser.parse(parser)


class _FileParser:
    def __init__(self, accepted_file_relativities: RelOptionsConfiguration):
        self._path_parser = parse_path.PathParser(
            RelOptionArgumentConfiguration(
                accepted_file_relativities,
                defs.SOURCE_FILE_ARGUMENT_NAME.name,
                True,
            )
        )

    def parse(self, file_option: Token, token_parser: TokenParser) -> StringSourceSdv:
        path = self._path_parser.parse_from_token_parser(token_parser)
        file_source = sdvs.PathStringSourceSdv(path)
        optional_transformer = parse_transformation_option.parse_optional_option__optional(token_parser)

        return (
            file_source
            if optional_transformer is None
            else
            sdvs.TransformedStringSourceSdv(
                file_source,
                optional_transformer,
            )
        )


class _ProgramOutputParser:
    def __init__(self, output_file_to_capture: ProcOutputFile):
        self._output_file_to_capture = output_file_to_capture

    def parse(self, program_option: Token, token_parser: TokenParser) -> StringSourceSdv:
        is_ignore_exit_code = token_parser.consume_optional_option(defs.IGNORE_EXIT_CODE)
        program = _PROGRAM_PARSER.parse_from_token_parser(token_parser)
        return sdvs.ProgramOutputStringSourceSdv(
            program_option.string,
            is_ignore_exit_code,
            self._output_file_to_capture,
            program,
        )


def _parse_here_doc(here_doc_start_token: Token, parser: TokenParser) -> StringSourceSdv:
    return _of_string(
        parse_here_document.parse_document_of_start_str(here_doc_start_token.string, parser, False)
    )


def _parse_string(parser: TokenParser) -> StringSourceSdv:
    return _of_string(parse_string_from_token_parser(parser))


def _of_string(contents: StringSdv) -> StringSourceSdv:
    return sdvs.ConstantStringStringSourceSdv(contents)


_PROGRAM_PARSER = parse_program.program_parser(
    must_be_on_current_line=False,
)
