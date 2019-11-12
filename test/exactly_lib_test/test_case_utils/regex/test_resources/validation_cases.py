from typing import List, Sequence

from exactly_lib.symbol.data import path_resolvers
from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.test_case_utils.regex.parse_regex import is_reference_to_valid_regex_string_part
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationExpectation
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class RegexValidationCase:
    def __init__(self,
                 case_name: str,
                 regex_string: str,
                 symbols: List[NameAndValue[SymbolValueResolver]],
                 reference_assertions: List[ValueAssertion[SymbolReference]],
                 expectation: ValidationExpectation,
                 ):
        self.case_name = case_name
        self.regex_string = regex_string
        self.symbols = symbols
        self.reference_assertions = reference_assertions
        self.expectation = expectation


def failing_regex_validation_cases(symbol_in_regex_name: str = 'symbol_in_regex') -> Sequence[RegexValidationCase]:
    post_sds_path = NameAndValue(
        symbol_in_regex_name,
        path_resolvers.of_rel_option(RelOptionType.REL_ACT)
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
