from typing import Sequence, TypeVar

from exactly_lib.definitions import logic
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression.grammar_elements import OperatorExpressionDescriptionFromFunctions
from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs, symbol_reference, parse_constant
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.name import NameWithGenderWithFormatting
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.textformat_parser import TextParser

MODEL = TypeVar('MODEL')


def new_grammar(concept: grammar.Concept,
                model: NameWithGenderWithFormatting,
                value_type: ValueType,
                simple_expressions: Sequence[NameAndValue[grammar.SimpleExpression[MatcherSdv[MODEL]]]],
                ) -> grammar.Grammar[MatcherSdv[MODEL]]:
    tp = TextParser({
        'model': model,
    })

    all_simple_expressions = list(simple_expressions) + [parse_constant.CONSTANT_PRIMITIVE]

    def mk_reference(symbol_name: str) -> MatcherSdv[MODEL]:
        return symbol_reference.MatcherReferenceSdv(symbol_name, value_type)

    return grammar.Grammar(
        concept,
        mk_reference=mk_reference,
        simple_expressions=all_simple_expressions,
        complex_expressions=[
            NameAndValue(
                logic.AND_OPERATOR_NAME,
                grammar.ComplexExpression(combinator_sdvs.Conjunction,
                                          OperatorExpressionDescriptionFromFunctions(
                                              tp.fnap__fun(_AND_SED_DESCRIPTION)
                                          ))
            ),
            NameAndValue(
                logic.OR_OPERATOR_NAME,
                grammar.ComplexExpression(combinator_sdvs.Disjunction,
                                          OperatorExpressionDescriptionFromFunctions(
                                              tp.fnap__fun(_OR_SED_DESCRIPTION)
                                          ))
            ),
        ],
        prefix_expressions=[
            NameAndValue(
                logic.NOT_OPERATOR_NAME,
                grammar.PrefixExpression(combinator_sdvs.Negation,
                                         OperatorExpressionDescriptionFromFunctions(
                                             tp.fnap__fun(_NOT_SED_DESCRIPTION)
                                         ))
            )
        ],
    )


_NOT_SED_DESCRIPTION = """\
Matches {model:s} not matched by the given matcher.
"""

_AND_SED_DESCRIPTION = """\
Matches {model:s} matched by every matcher.
"""

_OR_SED_DESCRIPTION = """\
Matches {model:s} matched by any matcher.
"""
