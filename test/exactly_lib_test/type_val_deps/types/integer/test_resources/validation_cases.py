from typing import List, Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.validation import validation
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions, Expectation
from exactly_lib_test.type_val_deps.types.integer.test_resources.references import \
    is_reference_to_symbol_in_expression
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolContext


class IntegerValidationCase:
    def __init__(self,
                 case_name: str,
                 integer_expr_string: str,
                 symbols: List[SymbolContext],
                 reference_assertions: List[Assertion[SymbolReference]],
                 expectations: Expectation,
                 assertions: ValidationAssertions,
                 ):
        self.case_name = case_name
        self.integer_expr_string = integer_expr_string
        self.symbols = symbols
        self.reference_assertions = reference_assertions
        self.expectations = expectations
        self.assertions = assertions

    @property
    def symbol_table(self) -> SymbolTable:
        return SymbolContext.symbol_table_of_contexts(self.symbols)

    @property
    def symbol_references_expectation(self) -> Assertion[Sequence[SymbolReference]]:
        return asrt.matches_sequence(self.reference_assertions)


def failing_integer_validation_cases(symbol_in_integer_name: str = 'symbol_in_integer'
                                     ) -> Sequence[IntegerValidationCase]:
    non_int_string_symbol = StringSymbolContext.of_constant(
        symbol_in_integer_name,
        'tre'
    )

    non_iterable_string_symbol = StringSymbolContext.of_constant(
        symbol_in_integer_name,
        '1'
    )

    constant_string_cases = [
        IntegerValidationCase('failing validation/pre sds: ' + expr_str,
                              expr_str,
                              [],
                              [],
                              validation.PRE_SDS_FAILURE_EXPECTATION,
                              validation.ValidationAssertions.pre_sds_fails__w_any_msg(),
                              )
        for expr_str in
        _PRE_SDS_VALIDATION_FAILURE__CONSTANT_STRINGS
    ]

    string_with_symbol_cases = [
        IntegerValidationCase('failing validation/pre sds: non-int string ref',
                              symbol_reference_syntax_for_name(non_int_string_symbol.name),
                              [non_int_string_symbol],
                              [is_reference_to_symbol_in_expression(non_int_string_symbol.name)],
                              validation.PRE_SDS_FAILURE_EXPECTATION,
                              ValidationAssertions.pre_sds_fails__w_any_msg(),
                              ),
        IntegerValidationCase('failing validation/pre sds: non-iterable string ref',
                              'len({})'.format(symbol_reference_syntax_for_name(non_iterable_string_symbol.name)),
                              [non_iterable_string_symbol],
                              [is_reference_to_symbol_in_expression(non_iterable_string_symbol.name)],
                              validation.PRE_SDS_FAILURE_EXPECTATION,
                              ValidationAssertions.pre_sds_fails__w_any_msg(),
                              ),
    ]

    return constant_string_cases + string_with_symbol_cases


_PRE_SDS_VALIDATION_FAILURE__CONSTANT_STRINGS = [
    'not_an_int',
    '1+not_an_int',
    '1.5',
    '(1',
]
