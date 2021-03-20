from typing import Callable, Optional

from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.impls.types.expression import grammar as _expr_grammar
from exactly_lib.impls.types.expression import parser as ep
from exactly_lib.impls.types.files_source import syntax
from exactly_lib.section_document.element_parsers.token_stream_parser import ParserFromTokens, TokenParser
from exactly_lib.type_val_deps.types.files_source import reference
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from exactly_lib.util.name_and_value import NameAndValue
from . import documentation, defs
from .impl import parse_file_list, parse_copy
from ..expression.parser import GrammarParsers


def parsers(must_be_on_current_line: bool = False) -> GrammarParsers[FilesSourceSdv]:
    return ep.parsers_for_must_be_on_current_line(grammar())[must_be_on_current_line]


def grammar() -> _expr_grammar.Grammar[FilesSourceSdv]:
    return _grammar(FullFilesSourceParser())


class FullFilesSourceParser(ParserFromTokens[FilesSourceSdv]):
    def __init__(self):
        self._parser: Optional[Callable[[TokenParser], FilesSourceSdv]] = None

    def parse(self, token_parser: TokenParser) -> FilesSourceSdv:
        self._construct_parser()
        return self._parser(token_parser)

    def _construct_parser(self):
        if self._parser is None:
            self._parser = parsers(False).full.parse_from_token_parser


_GRAMMAR_CONCEPT = _expr_grammar.Concept(
    name=types.FILES_SOURCE_TYPE_INFO.name,
    type_system_type_name=types.FILES_SOURCE_TYPE_INFO.identifier,
    syntax_element_name=syntax_elements.FILES_SOURCE_SYNTAX_ELEMENT.argument,
)

_COPY__SRC_PATH_ARG = syntax_elements.PATH_SYNTAX_ELEMENT

_DESCRIPTION_OF_FILE_LIST = documentation.FileListSyntaxDescription()
_DESCRIPTION_OF_COPY = documentation.CopySyntaxDescription(_COPY__SRC_PATH_ARG)


def _grammar(parser_of_nested: ParserFromTokens[FilesSourceSdv]) -> _expr_grammar.Grammar[FilesSourceSdv]:
    copy_src_dir_arg_conf = defs.src_dir_path_argument(_COPY__SRC_PATH_ARG.singular_name)

    return _expr_grammar.Grammar(
        concept=_GRAMMAR_CONCEPT,
        mk_reference=reference.ReferenceSdv,
        primitives=(
            NameAndValue(
                syntax.FILE_LIST_BEGIN,
                _expr_grammar.Primitive(
                    parse_file_list.Parser(parser_of_nested).parse,
                    _DESCRIPTION_OF_FILE_LIST,
                )
            ),
            NameAndValue(
                syntax.COPY_CONTENTS_OF_EXISTING_DIR,
                _expr_grammar.Primitive(
                    parse_copy.Parser(copy_src_dir_arg_conf).parse,
                    _DESCRIPTION_OF_COPY,
                )
            ),
        ),
        infix_operators_in_order_of_increasing_precedence=(),
        prefix_operators=(),
        custom_reserved_words=tuple(syntax.FILE_TYPE_TOKENS.values())
    )
