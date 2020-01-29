from typing import Sequence

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.definitions import formatting
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.documentation import relative_path_options_documentation
from exactly_lib.test_case_utils.documentation.string_or_here_doc_or_file import StringOrHereDocOrFile
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs
from exactly_lib.test_case_utils.parse import parse_here_doc_or_path, parse_path
from exactly_lib.test_case_utils.string_matcher.impl import equality
from exactly_lib.type_system.logic.string_matcher import GenericStringMatcherSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

_EXPECTED_SYNTAX_ELEMENT_FOR_EQUALS = 'EXPECTED'

EXPECTED_FILE_REL_OPT_ARG_CONFIG = parse_here_doc_or_path.CONFIGURATION


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    return StringMatcherSdv(
        combinator_sdvs.of_expectation_type(
            parse__generic(token_parser),
            expectation_type
        )
    )


def parse__generic(token_parser: TokenParser) -> GenericStringMatcherSdv:
    token_parser.require_has_valid_head_token(_EXPECTED_SYNTAX_ELEMENT_FOR_EQUALS)
    expected_contents = parse_here_doc_or_path.parse_from_token_parser(
        token_parser,
        EXPECTED_FILE_REL_OPT_ARG_CONFIG,
        consume_last_here_doc_line=False)

    return equality.sdv__generic(expected_contents)


class Description(grammar.SimpleExpressionDescription):
    def __init__(self):
        self._string_or_here_doc_or_file_arg = StringOrHereDocOrFile(
            _EXPECTED_PATH_NAME,
            _RELATIVITY_OF_EXPECTED_PATH_NAME,
            parse_path.all_rel_options_config(_EXPECTED_PATH_NAME),
            the_path_of('the file that contains the expected contents.')
        )

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return self._string_or_here_doc_or_file_arg.argument_usage(
            a.Multiplicity.MANDATORY),

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'HERE_DOCUMENT': formatting.syntax_element_(syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT),
            'SYMBOL_REFERENCE_SYNTAX_ELEMENT': syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name,
            'expected_file_arg': self._string_or_here_doc_or_file_arg.path_name,
        })
        return tp.fnap(_DESCRIPTION)

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return [
            relative_path_options_documentation.path_element_2(
                self._string_or_here_doc_or_file_arg.path_argument_configuration
            )
        ]

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return self._string_or_here_doc_or_file_arg.see_also_targets()


_EXPECTED_PATH_NAME = 'PATH-OF-EXPECTED'
_RELATIVITY_OF_EXPECTED_PATH_NAME = 'RELATIVITY-OF-EXPECTED-PATH'

_DESCRIPTION = """\
Matches if the string is equal to a given
string, {HERE_DOCUMENT} or contents of a file.


Any {SYMBOL_REFERENCE_SYNTAX_ELEMENT} appearing in the file {expected_file_arg} is NOT substituted.
"""
