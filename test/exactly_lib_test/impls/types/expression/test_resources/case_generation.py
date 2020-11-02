from typing import Sequence, List

from exactly_lib.impls.types.expression.grammar import Grammar
from exactly_lib_test.impls.types.expression.test_resources import test_grammars as ast
from exactly_lib_test.impls.types.expression.test_resources.ex_arr import SourceCase, Arrangement, Expectation
from exactly_lib_test.test_resources.test_utils import NArrEx


def current_line_case_variants_for_grammar(expected_expression: ast.Expr,
                                           grammar: Grammar,
                                           source_cases: Sequence[SourceCase],
                                           ) -> List[NArrEx[Arrangement, Expectation]]:
    ret_val = [
        NArrEx(
            the_source_case.name + ' / must_be_on_current_line=True',
            Arrangement(
                grammar=grammar,
                source=the_source_case.parse_source,
                must_be_on_current_line=True,
            ),
            Expectation(
                expression=expected_expression,
                source=the_source_case.assertion,
            )
        )
        for the_source_case in source_cases
    ]

    ret_val += [
        NArrEx(
            the_source_case.name + ' / must_be_on_current_line=False',
            Arrangement(
                grammar=grammar,
                source=the_source_case.parse_source,
                must_be_on_current_line=False,
            ),
            Expectation(
                expression=expected_expression,
                source=the_source_case.assertion,
            )
        )
        for the_source_case in source_cases
    ]

    ret_val += [
        for_added_empty_first_line(expected_expression, grammar, the_source_case)
        for the_source_case in source_cases
    ]

    return ret_val


def for_added_empty_first_line(expected_expression: ast.Expr,
                               the_grammar: Grammar,
                               src_case: SourceCase) -> NArrEx[Arrangement, Expectation]:
    case_for_empty_first_line = src_case.for_added_empty_first_line()
    return NArrEx(
        case_for_empty_first_line.name + ' / must_be_on_current_line=False',
        Arrangement(
            grammar=the_grammar,
            source=case_for_empty_first_line.parse_source,
            must_be_on_current_line=False,
        ),
        Expectation(
            expression=expected_expression,
            source=case_for_empty_first_line.assertion,
        )
    )
