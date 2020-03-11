from typing import Sequence

from exactly_lib.symbol.logic.files_matcher import FilesMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.logic.files_matcher import GenericFilesMatcherSdv, FilesMatcher
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref, \
    files_matcher_stv_constant_test_impl
from exactly_lib_test.symbol.test_resources.symbols_setup import SdvSymbolContext, SymbolTableValue
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_wo_tcds, \
    PrimAndExeExpectation
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.test_resources import pre_or_post_sds_value_validator
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationActual, ValidationAssertions
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class FilesMatcherSymbolTableValue(SymbolTableValue[FilesMatcherStv]):
    @staticmethod
    def of_generic(sdv: GenericFilesMatcherSdv) -> 'FilesMatcherSymbolTableValue':
        return FilesMatcherSymbolTableValue(FilesMatcherStv(sdv))

    @staticmethod
    def of_primitive(primitive: FilesMatcher) -> 'FilesMatcherSymbolTableValue':
        return FilesMatcherSymbolTableValue.of_generic(matchers.sdv_from_primitive_value(primitive))

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_reference_to_files_matcher__ref(symbol_name)


class FilesMatcherSymbolContext(SdvSymbolContext[FilesMatcherStv]):
    def __init__(self,
                 name: str,
                 value: FilesMatcherSymbolTableValue,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdtv(name: str, sdtv: FilesMatcherStv) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext(
            name,
            FilesMatcherSymbolTableValue(sdtv)
        )

    @staticmethod
    def of_generic(name: str, sdv: GenericFilesMatcherSdv) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext(
            name,
            FilesMatcherSymbolTableValue.of_generic(sdv)
        )

    @staticmethod
    def of_primitive(name: str, primitive: FilesMatcher) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext(
            name,
            FilesMatcherSymbolTableValue.of_primitive(primitive)
        )


class ValidationCase:
    def __init__(self,
                 expectation: ValidationAssertions,
                 actual: ValidationActual,
                 symbol_name: str = 'files_matcher_symbol',
                 ):
        self._expectation = expectation
        self._symbol_context = FilesMatcherSymbolContext.of_sdtv(
            symbol_name,
            files_matcher_stv_constant_test_impl(
                True,
                validator=pre_or_post_sds_value_validator.constant_validator(actual),
            ),
        )

    @property
    def symbol_context(self) -> FilesMatcherSymbolContext:
        return self._symbol_context

    @property
    def expectation(self) -> ValidationAssertions:
        return self._expectation


def failing_validation_cases(symbol_name: str = 'files_matcher_symbol'
                             ) -> Sequence[NameAndValue[ValidationCase]]:
    return [
        NameAndValue(
            case.name,
            ValidationCase(case.expected,
                           case.actual,
                           symbol_name)
        )
        for case in validation.failing_validation_cases()
    ]


def failing_validation_cases__multi_exe(symbol_name: str = 'files_matcher_symbol'):
    return [
        NExArr(
            case.name,
            PrimAndExeExpectation.of_exe(
                validation=case.value.expectation,
            ),
            arrangement_wo_tcds(
                symbols=case.value.symbol_context.symbol_table,
            ),
        )
        for case in failing_validation_cases(symbol_name)
    ]
