from typing import List, Sequence

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_utils.condition.integer.test_resources.integer_sdv import \
    is_reference_to_symbol_in_expression
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationExpectation
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class IntegerValidationCase:
    def __init__(self,
                 case_name: str,
                 integer_expr_string: str,
                 symbols: List[NameAndValue[SymbolDependentValue]],
                 reference_assertions: List[ValueAssertion[SymbolReference]],
                 expectation: ValidationExpectation,
                 ):
        self.case_name = case_name
        self.integer_expr_string = integer_expr_string
        self.symbols = symbols
        self.reference_assertions = reference_assertions
        self.expectation = expectation

    @property
    def symbol_table(self) -> SymbolTable:
        return symbol_utils.symbol_table_from_name_and_sdvs(self.symbols)

    @property
    def symbol_references_expectation(self) -> ValueAssertion[Sequence[SymbolReference]]:
        return asrt.matches_sequence(self.reference_assertions)


def failing_integer_validation_cases(symbol_in_integer_name: str = 'symbol_in_integer'
                                     ) -> Sequence[IntegerValidationCase]:
    non_int_string_symbol = NameAndValue(
        symbol_in_integer_name,
        string_sdvs.str_constant('tre')
    )

    non_iterable_string_symbol = NameAndValue(
        symbol_in_integer_name,
        string_sdvs.str_constant('1')
    )

    constant_string_cases = [
        IntegerValidationCase('failing validation/pre sds: ' + expr_str,
                              expr_str,
                              [],
                              [],
                              validation.pre_sds_validation_fails__w_any_msg(),
                              )
        for expr_str in
        _PRE_SDS_VALIDATION_FAILURE__CONSTANT_STRINGS
    ]

    string_with_symbol_cases = [
        IntegerValidationCase('failing validation/pre sds: non-int string ref',
                              symbol_reference_syntax_for_name(non_int_string_symbol.name),
                              [non_int_string_symbol],
                              [is_reference_to_symbol_in_expression(non_int_string_symbol.name)],
                              validation.pre_sds_validation_fails__w_any_msg(),
                              ),
        IntegerValidationCase('failing validation/pre sds: non-iterable string ref',
                              'len({})'.format(symbol_reference_syntax_for_name(non_iterable_string_symbol.name)),
                              [non_iterable_string_symbol],
                              [is_reference_to_symbol_in_expression(non_iterable_string_symbol.name)],
                              validation.pre_sds_validation_fails__w_any_msg(),
                              ),
    ]

    return constant_string_cases + string_with_symbol_cases


_PRE_SDS_VALIDATION_FAILURE__CONSTANT_STRINGS = [
    'not_an_int',
    '1+not_an_int',
    '1.5',
    '(1',
]
