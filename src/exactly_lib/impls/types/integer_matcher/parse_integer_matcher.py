from typing import Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.condition.comparators import ComparisonOperator
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.expression import parser as ep
from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.impls.types.integer import parse_integer
from exactly_lib.impls.types.matcher import standard_expression_grammar
from exactly_lib.impls.types.matcher.impls import comparison_matcher, combinator_matchers
from exactly_lib.impls.types.matcher.impls.comparison_matcher import ComparisonMatcherSdv
from exactly_lib.impls.types.matcher.impls.operand_object import ObjectSdvOfOperandSdv
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.integer_matcher import IntegerMatcherSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import details
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parsers(must_be_on_current_line: bool = False) -> GrammarParsers[IntegerMatcherSdv]:
    return _PARSERS_FOR_MUST_BE_ON_CURRENT_LINE[must_be_on_current_line]


_INTEGER_PARSER = parse_integer.MandatoryIntegerParser()


class _ComparisonParser(ParserFromTokens[IntegerMatcherSdv]):
    def __init__(self, operator: ComparisonOperator):
        self._config = comparison_matcher.IntModelConstructionConfig(
            comparison_matcher.Config(
                syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name,
                operator,
                lambda x: details.String(x),
            )
        )

    def parse(self, token_parser: TokenParser) -> IntegerMatcherSdv:
        rhs = _INTEGER_PARSER.parse(token_parser)
        return ComparisonMatcherSdv(
            self._config,
            ObjectSdvOfOperandSdv(rhs),
        )


class _ComparisonSyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    def __init__(self, operator: ComparisonOperator):
        self._operator = operator

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            syntax_elements.INTEGER_SYNTAX_ELEMENT.single_mandatory
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'model': matcher_model.INTEGER_MATCHER_MODEL,
            'operator': self._operator.description,
            'LHS': syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name,
        })
        return tp.fnap(_COMPARISON_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return syntax_elements.INTEGER_SYNTAX_ELEMENT.cross_reference_target,


GRAMMAR = standard_expression_grammar.new_grammar(
    concept=grammar.Concept(
        name=types.INTEGER_MATCHER_TYPE_INFO.name,
        type_system_type_name=types.INTEGER_MATCHER_TYPE_INFO.identifier,
        syntax_element_name=syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.argument,
    ),
    model=matcher_model.INTEGER_MATCHER_MODEL,
    value_type=ValueType.INTEGER_MATCHER,
    simple_expressions=[
        NameAndValue(
            operator.name,
            grammar.Primitive(
                _ComparisonParser(operator).parse,
                _ComparisonSyntaxDescription(operator),
            )
        )
        for operator in comparators.ALL_OPERATORS
    ],
    model_freezer=combinator_matchers.no_op_freezer,
)

_PARSERS_FOR_MUST_BE_ON_CURRENT_LINE = ep.parsers_for_must_be_on_current_line(GRAMMAR)

_COMPARISON_DESCRIPTION = """\
Matches {model:s} {operator} {LHS}.
"""
