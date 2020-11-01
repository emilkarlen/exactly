from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolUsage
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case_utils.files_matcher.impl.base_class import FilesMatcherDdvImplBase, FilesMatcherImplBase
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.files_matcher import FilesMatcherAdv, FilesMatcherDdv
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel, FilesMatcher
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.sym_ref.test_resources.restrictions_assertions import is_value_type_restriction


class FilesMatcherTestImpl(FilesMatcherImplBase):
    def __init__(self, result: bool = True):
        super().__init__()
        self._result = result

    @property
    def name(self) -> str:
        return str(type(self)) + ': test impl with constant ' + str(self._result)

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        return (
            self._new_tb()
                .build_result(self._result)
        )


class FilesMatcherNumFilesTestImpl(FilesMatcherImplBase):
    def __init__(self, expected_num_files: int):
        super().__init__()
        self._expected_num_files = expected_num_files

    @property
    def name(self) -> str:
        return str(type(self)) + ': test impl num-files ==  ' + str(self._expected_num_files)

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        return (
            self._new_tb()
                .build_result(
                len(list(model.files())) == self._expected_num_files
            )
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

    def value_of_any_dependency(self, tcds: TestCaseDs) -> FilesMatcherAdv:
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


IS_FILES_MATCHER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.FILES_MATCHER)


def is_reference_to_files_matcher__usage(name_of_matcher: str) -> ValueAssertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                            IS_FILES_MATCHER_REFERENCE_RESTRICTION)


def is_reference_to_files_matcher(name_of_matcher: str
                                  ) -> ValueAssertion[SymbolReference]:
    return asrt_sym_usage.matches_reference__ref(asrt.equals(name_of_matcher),
                                                 IS_FILES_MATCHER_REFERENCE_RESTRICTION)
