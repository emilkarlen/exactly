from typing import List, Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.data.test_resources.path import PathDdvSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.regex.parse_regex import is_reference_to_valid_regex_string_part
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationAssertions
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class RegexValidationCase:
    def __init__(self,
                 case_name: str,
                 regex_string: str,
                 symbols: List[SymbolContext],
                 reference_assertions: List[ValueAssertion[SymbolReference]],
                 expectation: ValidationAssertions,
                 ):
        self.case_name = case_name
        self.regex_string = regex_string
        self.symbols = symbols
        self.reference_assertions = reference_assertions
        self.expectation = expectation

    @property
    def symbol_table(self) -> SymbolTable:
        return SymbolContext.symbol_table_of_contexts(self.symbols)


def failing_regex_validation_cases(symbol_in_regex_name: str = 'symbol_in_regex') -> Sequence[RegexValidationCase]:
    post_sds_path = PathDdvSymbolContext.of_no_suffix(
        symbol_in_regex_name,
        RelOptionType.REL_ACT
    )
    return [
        RegexValidationCase(
            'failing validation/pre sds',
            '*',
            [],
            [],
            validation.pre_sds_validation_fails__w_any_msg(),
        ),
        RegexValidationCase(
            'failing validation/post sds',
            '*' + symbol_reference_syntax_for_name(post_sds_path.name),
            [post_sds_path],
            [is_reference_to_valid_regex_string_part(post_sds_path.name)],
            validation.post_sds_validation_fails__w_any_msg(),
        ),
    ]
