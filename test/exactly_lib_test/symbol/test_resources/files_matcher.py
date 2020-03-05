from typing import Sequence

from exactly_lib.symbol.logic.files_matcher import FilesMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolUsage
from exactly_lib.test_case_file_structure import ddv_validation
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.files_matcher.impl.base_class import FilesMatcherDdvImplBase, FilesMatcherImplBase
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcher, FilesMatcherDdv, \
    FilesMatcherAdv
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def arbitrary_sdv() -> FilesMatcherStv:
    return files_matcher_sdv_constant_test_impl(True)


class FilesMatcherTestImpl(FilesMatcherImplBase):
    def __init__(self, result: bool = True):
        super().__init__()
        self._result = result

    @property
    def name(self) -> str:
        return str(type(self)) + ': test impl with constant ' + str(self._result)

    @property
    def negation(self) -> FilesMatcher:
        return FilesMatcherTestImpl(not self._result)

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        return (
            self._new_tb()
                .build_result(self._result)
        )


class FilesMatcherDdvConstantTestImpl(FilesMatcherDdvImplBase):
    def __init__(self,
                 constant: FilesMatcherAdv,
                 validator: DdvValidator = ddv_validation.constant_success_validator(),
                 ):
        self._constant = constant
        self._validator = validator

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> FilesMatcherAdv:
        return self._constant


def constant_ddv(matcher: FilesMatcher) -> FilesMatcherDdv:
    return FilesMatcherDdvConstantTestImpl(
        advs.ConstantMatcherAdv(matcher)
    )


def value_with_result(result: bool,
                      validator: DdvValidator = ddv_validation.constant_success_validator()) -> FilesMatcherDdv:
    return FilesMatcherDdvConstantTestImpl(
        advs.ConstantMatcherAdv(FilesMatcherTestImpl(result)),
        validator,
    )


def files_matcher_sdv_constant_test_impl(resolved_value: bool = True,
                                         references: Sequence[SymbolReference] = (),
                                         validator: DdvValidator = ddv_validation.constant_success_validator()) -> FilesMatcherStv:
    return FilesMatcherStv(matchers.sdv_from_bool(resolved_value,
                                                  references,
                                                  validator))


def files_matcher_sdv_constant_ddv_test_impl(resolved_value: FilesMatcherDdv,
                                             references: Sequence[SymbolReference] = ()) -> FilesMatcherStv:
    return FilesMatcherStv(matchers.MatcherSdvOfConstantDdvTestImpl(resolved_value,
                                                                    references))


IS_FILES_MATCHER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.FILES_MATCHER)


def is_reference_to_files_matcher(name_of_matcher: str) -> ValueAssertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                            IS_FILES_MATCHER_REFERENCE_RESTRICTION)


def is_reference_to_files_matcher__ref(name_of_matcher: str
                                       ) -> ValueAssertion[SymbolReference]:
    return asrt_sym_usage.matches_reference__ref(asrt.equals(name_of_matcher),
                                                 IS_FILES_MATCHER_REFERENCE_RESTRICTION)
