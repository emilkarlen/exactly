from typing import Sequence

from exactly_lib.impls.types.files_condition import files_conditions
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources import file_matchers as fm_sdvs, \
    validation_cases as fm_validation_cases
from exactly_lib_test.type_val_deps.types.files_condition.test_resources.symbol_context import \
    FilesConditionSymbolContext


class ValidationCase:
    def __init__(self,
                 fm_validation_case: fm_validation_cases.ValidationCase,
                 symbol_name: str,
                 ):
        self._expectation = fm_validation_case.expectation
        self._symbol_context = FilesConditionSymbolContext.of_sdv(
            symbol_name,
            files_conditions.new_constant([
                (string_sdvs.str_constant('a_valid_file_name'),
                 fm_sdvs.new_reference(fm_validation_case.symbol_context.name))
            ]),
        )
        self._symbol_table = SymbolContext.symbol_table_of_contexts([
            self._symbol_context,
            fm_validation_case.symbol_context,
        ])

    @property
    def symbol_context(self) -> FilesConditionSymbolContext:
        return self._symbol_context

    @property
    def symbol_table(self) -> SymbolTable:
        return self._symbol_table

    @property
    def expectation(self) -> ValidationAssertions:
        return self._expectation


def failing_validation_cases(fc_symbol_name: str = 'files_condition_symbol',
                             fm_symbol_name: str = 'file_matcher_symbol') -> Sequence[NameAndValue[ValidationCase]]:
    return [
        NameAndValue(
            case.name,
            ValidationCase(case.value,
                           fc_symbol_name)
        )
        for case in fm_validation_cases.failing_validation_cases(fm_symbol_name)
    ]
