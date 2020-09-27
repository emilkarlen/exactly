from typing import Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.test_case_utils.expression import grammar, parser as ep
from exactly_lib.test_case_utils.expression.parser import GrammarParsers
from exactly_lib.test_case_utils.line_matcher.impl import matches_regex, line_number
from exactly_lib.test_case_utils.matcher import standard_expression_grammar
from exactly_lib.type_system.logic.line_matcher import FIRST_LINE_NUMBER, LineMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parsers(must_be_on_current_line: bool = False) -> GrammarParsers[LineMatcherSdv]:
    return _PARSERS_FOR_MUST_BE_ON_CURRENT_LINE[must_be_on_current_line]


_TP = TextParser({
    'REG_EX': syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name,
    'INTEGER_MATCHER': syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name,
    'FIRST_LINE_NUMBER': FIRST_LINE_NUMBER,
    'MODEL': matcher_model.LINE_MATCHER_MODEL,
})

_REGEX_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} that contain a string that matches {REG_EX}.
"""

_LINE_NUMBER_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} who's line number matches {INTEGER_MATCHER}.


Line numbers start at {FIRST_LINE_NUMBER}.
"""


class _RegexSyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            syntax_elements.REGEX_SYNTAX_ELEMENT.single_mandatory,
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_REGEX_MATCHER_SED_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [syntax_elements.REGEX_SYNTAX_ELEMENT.cross_reference_target]


class _LineNumberSyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_LINE_NUMBER_MATCHER_SED_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.cross_reference_target]


_CONCEPT = grammar.Concept(
    types.LINE_MATCHER_TYPE_INFO.name,
    types.LINE_MATCHER_TYPE_INFO.identifier,
    syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.argument,
)

GRAMMAR = standard_expression_grammar.new_grammar(
    _CONCEPT,
    model=matcher_model.LINE_MATCHER_MODEL,
    value_type=ValueType.LINE_MATCHER,
    simple_expressions=(
        NameAndValue(
            line_matcher.REGEX_MATCHER_NAME,
            grammar.Primitive(matches_regex.parse,
                              _RegexSyntaxDescription())
        ),
        NameAndValue(
            line_matcher.LINE_NUMBER_MATCHER_NAME,
            grammar.Primitive(line_number.parse_line_number,
                              _LineNumberSyntaxDescription())
        ),
    ),
)

_PARSERS_FOR_MUST_BE_ON_CURRENT_LINE = ep.parsers_for_must_be_on_current_line(GRAMMAR)
