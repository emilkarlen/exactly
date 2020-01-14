from typing import Sequence

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.matcher.impls import parse_integer_matcher, combinator_sdvs
from exactly_lib.test_case_utils.string_matcher.impl import num_lines
from exactly_lib.type_system.logic.string_matcher import GenericStringMatcherSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    return StringMatcherSdv(
        combinator_sdvs.of_expectation_type(
            parse__generic(token_parser),
            expectation_type
        )
    )


def parse__generic(token_parser: TokenParser) -> GenericStringMatcherSdv:
    matcher = parse_integer_matcher.parse(
        token_parser,
        ExpectationType.POSITIVE,
        parse_integer_matcher.validator_for_non_negative,
    )
    return num_lines.sdv__generic(matcher)


class Description(grammar.SimpleExpressionDescription):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory,

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'INTEGER_MATCHER': syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name,
        })
        return tp.fnap(_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return syntax_elements.REGEX_SYNTAX_ELEMENT.cross_reference_target,


_DESCRIPTION = """\
Matches if the number of lines of the string matches {INTEGER_MATCHER}.
"""
