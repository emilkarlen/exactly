from typing import Mapping

from exactly_lib.definitions import expression
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression.grammar import EXPR
from exactly_lib.test_case_utils.expression.grammar_elements import OperatorExpressionDescriptionFromFunctions
from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs, symbol_reference
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.name import NameWithGenderWithFormatting
from exactly_lib.util.textformat.textformat_parser import TextParser


def new_grammar(concept: grammar.Concept,
                model: NameWithGenderWithFormatting,
                value_type: ValueType,
                simple_expressions: Mapping[str, grammar.SimpleExpression[EXPR]],
                ) -> grammar.Grammar[EXPR]:
    tp = TextParser({
        'model': model,
    })

    def mk_reference(symbol_name: str) -> EXPR:
        return symbol_reference.MatcherReferenceSdv(symbol_name, value_type)

    return grammar.Grammar(
        concept,
        mk_reference=mk_reference,
        simple_expressions=simple_expressions,
        complex_expressions={
            expression.AND_OPERATOR_NAME:
                grammar.ComplexExpression(combinator_sdvs.Conjunction,
                                          OperatorExpressionDescriptionFromFunctions(
                                              tp.fnap__fun(_AND_SED_DESCRIPTION)
                                          )),
            expression.OR_OPERATOR_NAME:
                grammar.ComplexExpression(combinator_sdvs.Disjunction,
                                          OperatorExpressionDescriptionFromFunctions(
                                              tp.fnap__fun(_OR_SED_DESCRIPTION)
                                          )),
        },
        prefix_expressions={
            expression.NOT_OPERATOR_NAME:
                grammar.PrefixExpression(combinator_sdvs.Negation,
                                         OperatorExpressionDescriptionFromFunctions(
                                             tp.fnap__fun(_NOT_SED_DESCRIPTION)
                                         ))
        },
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
