import functools

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.list_ import generic_parser, parse_list
from exactly_lib.impls.types.path import parse_path
from exactly_lib.impls.types.program import syntax_elements as _pgm_syntax_elements
from exactly_lib.impls.types.program.command import arguments_sdvs
from exactly_lib.impls.types.string_ import parse_string, parse_rich_string
from exactly_lib.section_document.element_parsers import token_stream_parsing as parsing
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import Parser, ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.symbol.sdv_structure import SymbolName
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.path import rel_opts_configuration
from exactly_lib.type_val_deps.types.path.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.util import either
from exactly_lib.util.either import Either
from exactly_lib.util.parse import token_matchers

REL_OPTIONS_CONF = rel_opts_configuration.RelOptionsConfiguration(
    rel_opts_configuration.RELATIVITY_VARIANTS_FOR_ALL_EXCEPT_RESULT,
    RelOptionType.REL_HDS_CASE)

REL_OPT_ARG_CONF = RelOptionArgumentConfiguration(
    REL_OPTIONS_CONF,
    syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT.singular_name,
    True)

_STRING_CONFIGURATION = parse_string.Configuration(syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT.singular_name,
                                                   reference_restrictions=None)


def parser() -> Parser[ArgumentsSdv]:
    return _PARSER


class _Parser(ParserFromTokenParserBase[ArgumentsSdv]):
    def __init__(self):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=False,
                         consume_last_line_if_is_at_eof_after_parse=False)
        self._elements_parser = generic_parser.ElementsUntilEndOfLineParser2(
            _ElementParser(),
            _MkElement(),
        )

    def parse_from_token_parser(self, token_parser: TokenParser) -> ArgumentsSdv:
        elements = self._elements_parser.parse(token_parser)
        return functools.reduce(_accumulate, elements, ArgumentsSdv.empty())


def _accumulate(x: ArgumentsSdv, y: ArgumentsSdv) -> ArgumentsSdv:
    return x.new_accumulated(y)


class _ElementParser(ParserFromTokens[Either[SymbolName, ArgumentsSdv]]):
    def __init__(self):
        self._string_or_sym_ref_parser = parse_rich_string.SymbolNameOrStringRichStringParser(_STRING_CONFIGURATION)
        self._element_choices = [
            parsing.TokenSyntaxSetup(
                token_matchers.is_option(_pgm_syntax_elements.EXISTING_FILE_OPTION_NAME),
                _parse_existing_file,
            ),
            parsing.TokenSyntaxSetup(
                token_matchers.is_option(_pgm_syntax_elements.EXISTING_DIR_OPTION_NAME),
                _parse_existing_dir,
            ),
            parsing.TokenSyntaxSetup(
                token_matchers.is_option(_pgm_syntax_elements.EXISTING_PATH_OPTION_NAME),
                _parse_existing_path,
            ),
        ]

    def parse(self, token_parser: TokenParser) -> Either[SymbolName, ArgumentsSdv]:
        return parsing.parse_mandatory_choice_with_default(
            token_parser,
            syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT.singular_name,
            self._element_choices,
            self._parse_plain_list_element,
        )

    def _parse_plain_list_element(self, token_parser: TokenParser) -> Either[SymbolName, ArgumentsSdv]:
        sym_ref_or_string = self._string_or_sym_ref_parser.parse_from_token_parser(token_parser)
        if sym_ref_or_string.is_left():
            return Either.of_left(sym_ref_or_string.left())
        else:
            return Either.of_right(
                ArgumentsSdv.new_without_validation(list_sdvs.from_string(sym_ref_or_string.right()))
            )


class _MkElement(either.Reducer[SymbolName, ArgumentsSdv, ArgumentsSdv]):
    def reduce_left(self, x: SymbolName) -> ArgumentsSdv:
        sym_ref_element = parse_list.symbol_reference_element(x)
        return ArgumentsSdv.new_without_validation(list_sdvs.from_elements([sym_ref_element]))

    def reduce_right(self, x: ArgumentsSdv) -> ArgumentsSdv:
        return x


_PATH_PARSER = parse_path.PathParser(REL_OPT_ARG_CONF)


def _parse_existing_file(token_parser: TokenParser) -> Either[SymbolName, ArgumentsSdv]:
    path = _PATH_PARSER.parse_from_token_parser(token_parser)
    return Either.of_right(
        arguments_sdvs.ref_to_file_that_must_exist(path, FileType.REGULAR)
    )


def _parse_existing_dir(token_parser: TokenParser) -> Either[SymbolName, ArgumentsSdv]:
    path = _PATH_PARSER.parse_from_token_parser(token_parser)
    return Either.of_right(
        arguments_sdvs.ref_to_file_that_must_exist(path, FileType.DIRECTORY)
    )


def _parse_existing_path(token_parser: TokenParser) -> Either[SymbolName, ArgumentsSdv]:
    path = _PATH_PARSER.parse_from_token_parser(token_parser)
    return Either.of_right(
        arguments_sdvs.ref_to_path_that_must_exist(path)
    )


_PARSER = _Parser()
