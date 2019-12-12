from typing import Sequence, Optional

from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.test_case_utils.files_matcher.impl import files_matchers
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcher, FilesMatcherConstructor, \
    FilesMatcherDdv
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def arbitrary_sdv() -> FilesMatcherSdv:
    return FilesMatcherSdvConstantTestImpl(True)


class FilesMatcherTestImpl(FilesMatcher):
    def __init__(self,
                 result: bool = True):
        self._result = result

    @property
    def name(self) -> str:
        return str(type(self)) + ': test impl with constant ' + str(self._result)

    @property
    def negation(self) -> FilesMatcher:
        return FilesMatcherTestImpl(not self._result)

    def matches_emr(self, files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        if self._result:
            return None
        else:
            return err_msg_resolvers.constant('test impl with constant ' + str(self._result))

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        return (
            self._new_tb()
                .build_result(self._result)
        )


class FilesMatcherDdvConstantTestImpl(FilesMatcherDdv):
    def __init__(self,
                 constant: FilesMatcherConstructor,
                 validator: DdvValidator = ddv_validation.constant_success_validator(),
                 ):
        self._constant = constant
        self._validator = validator

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> FilesMatcherConstructor:
        return self._constant


def constant_ddv(matcher: FilesMatcher) -> FilesMatcherDdv:
    return FilesMatcherDdvConstantTestImpl(
        files_matchers.ConstantConstructor(
            matcher
        )
    )


def value_with_result(result: bool,
                      validator: DdvValidator = ddv_validation.constant_success_validator()) -> FilesMatcherDdv:
    return FilesMatcherDdvConstantTestImpl(
        files_matchers.ConstantConstructor(
            FilesMatcherTestImpl(result)
        ),
        validator,
    )


class FilesMatcherSdvConstantTestImpl(FilesMatcherSdv):
    def __init__(self,
                 resolved_value: bool = True,
                 references: Sequence[SymbolReference] = (),
                 validator: DdvValidator = ddv_validation.constant_success_validator()):
        self._resolved_value = resolved_value
        self._references = list(references)
        self._validator = validator

    @property
    def resolved_value(self) -> bool:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        return value_with_result(self._resolved_value,
                                 self._validator)


class FilesMatcherSdvConstantDdvTestImpl(FilesMatcherSdv):
    def __init__(self,
                 resolved_value: FilesMatcherDdv,
                 references: Sequence[SymbolReference] = (),
                 ):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        return self._resolved_value


IS_FILES_MATCHER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.FILES_MATCHER)


def is_reference_to_files_matcher(name_of_matcher: str) -> ValueAssertion[su.SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                            IS_FILES_MATCHER_REFERENCE_RESTRICTION)


def is_reference_to_files_matcher__ref(name_of_matcher: str) -> ValueAssertion[su.SymbolReference]:
    return asrt_sym_usage.matches_reference__ref(asrt.equals(name_of_matcher),
                                                 IS_FILES_MATCHER_REFERENCE_RESTRICTION)
