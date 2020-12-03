import unittest
from typing import List, Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.integer_matcher.test_resources import symbol_reference as int_sym_refs
from exactly_lib_test.impls.types.line_matcher.test_resources import arguments_building as lm_arg
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_wo_tcds, Expectation, \
    ParseExpectation, ExecutionExpectation
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor as models
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check, \
    argument_building as st_arg
from exactly_lib_test.impls.types.test_resources import arguments_building as arg_rend
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext, \
    StringIntConstantSymbolContext
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source


class Case:
    def __init__(self,
                 model: List[str],
                 arguments: ArgumentElementsRenderer,
                 symbols: Sequence[SymbolContext],
                 expected_output_lines: List[str],
                 max_num_lines_from_iter: int,
                 ):
        self.model = model
        self.arguments = arguments
        self.symbols = symbols
        self.expected_output_lines = expected_output_lines
        self.max_num_lines_from_iter = max_num_lines_from_iter


def model_lines(num_lines: int) -> List[str]:
    return [
        'Line {}\n'.format(i + 1)
        for i in range(num_lines)
    ]


def check_cases(put: unittest.TestCase, cases: Sequence[Case]):
    for case in cases:
        with put.subTest(case.arguments.as_str):
            check(put, case)


def check_cases__named(put: unittest.TestCase, cases: Sequence[NameAndValue[Case]]):
    for case in cases:
        with put.subTest(case.name):
            check(put, case.value)


def check(put: unittest.TestCase, case: Case):
    integration_check.CHECKER__PARSE_SIMPLE__WO_IMPLICIT_MODEL_EVALUATION.check(
        put,
        case.arguments.as_remaining_source,
        _model_w_access_check(put, case.model, case.max_num_lines_from_iter),
        arrangement_wo_tcds(
            symbols=SymbolContext.symbol_table_of_contexts(case.symbols)
        ),
        Expectation(
            parse=ParseExpectation(
                source=asrt_source.is_at_end_of_line(1),
                symbol_references=SymbolContext.references_assertion_of_contexts(case.symbols)
            ),
            execution=ExecutionExpectation(
                main_result=asrt_string_source.matches__lines__check_just_as_lines(case.expected_output_lines)
            ),
        )
    )


class IntSymbol:
    def __init__(self, name: str):
        self.name = name

    def value(self, value: int) -> StringConstantSymbolContext:
        return StringIntConstantSymbolContext(
            self.name,
            value,
            default_restrictions=int_sym_refs.IS_INTEGER_STR_REFERENCE_RESTRICTIONS
        )


class ModelAndArguments:
    def __init__(self,
                 model: List[str],
                 arguments: ArgumentElementsRenderer,
                 ):
        self.model = model
        self.arguments = arguments

    def case(self,
             symbols: Sequence[StringConstantSymbolContext],
             max_num_lines_from_iter: int,
             expected_output_lines: List[int],
             ) -> Case:
        return Case(
            self.model,
            self.arguments,
            symbols,
            [
                self.model[n - 1]
                for n in expected_output_lines
            ],
            max_num_lines_from_iter,
        )

    def case__n(self,
                symbols: Sequence[StringConstantSymbolContext],
                max_num_lines_from_iter: int,
                expected_output_lines: List[int],
                ) -> NameAndValue[Case]:
        return NameAndValue(
            'args={}, symbols={}'.format(
                self.arguments.as_str,
                [
                    '{}={}'.format(sym.name, sym.str_value)
                    for sym in symbols
                ]
            ),
            Case(
                self.model,
                self.arguments,
                symbols,
                [
                    self.model[n - 1]
                    for n in expected_output_lines
                ],
                max_num_lines_from_iter,
            ))

    def equivalent_cases(self,
                         symbols_cases: Sequence[Sequence[StringConstantSymbolContext]],
                         max_num_lines_from_iter: int,
                         expected_output_lines: List[int],
                         ) -> List[Case]:
        return [
            self.case(symbols, max_num_lines_from_iter, expected_output_lines)
            for symbols in symbols_cases
        ]

    def equivalent_cases__n(self,
                            symbols_cases: Sequence[Sequence[StringConstantSymbolContext]],
                            max_num_lines_from_iter: int,
                            expected_output_lines: List[int],
                            ) -> List[NameAndValue[Case]]:
        return [
            self.case__n(symbols, max_num_lines_from_iter, expected_output_lines)
            for symbols in symbols_cases
        ]


def _model_w_access_check(put: unittest.TestCase,
                          lines: List[str],
                          max_num_lines_from_iter: int,
                          ) -> models.ModelConstructor:
    return models.of_lines__w_max_invocations__w_max_lines_from_iter(
        put,
        lines,
        max_num_lines_from_iter=max_num_lines_from_iter,
        max_as_lines_invocations=1,
    )


def filter_lm(line_matcher: ArgumentElementsRenderer) -> ArgumentElementsRenderer:
    return st_arg.Filter(st_arg.FilterLineMatcherVariant(line_matcher))


def filter_lm__within_parens(line_matcher: ArgumentElementsRenderer) -> ArgumentElementsRenderer:
    return st_arg.Filter(st_arg.FilterLineMatcherVariant(
        arg_rend.within_paren(line_matcher)
    ))


def filter_line_num(integer_matcher: ArgumentElementsRenderer) -> ArgumentElementsRenderer:
    return filter_lm(lm_arg.LineNum2(integer_matcher))


def _from_to(line_num_first: int, line_num_last: int) -> List[int]:
    return list(range(line_num_first, line_num_last + 1))
