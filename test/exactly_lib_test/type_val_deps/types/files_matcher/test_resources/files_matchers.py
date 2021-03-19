from exactly_lib.impls.types.files_matcher.impl.base_class import FilesMatcherDdvImplBase, FilesMatcherImplBase
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.files_matcher import FilesMatcherAdv, FilesMatcherDdv
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel, FilesMatcher
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult


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
                 validator: DdvValidator = ddv_validation.ConstantDdvValidator.new_success(),
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
                      validator: DdvValidator = ddv_validation.ConstantDdvValidator.new_success()) -> FilesMatcherDdv:
    return FilesMatcherDdvConstantTestImpl(
        advs.ConstantMatcherAdv(FilesMatcherTestImpl(result)),
        validator,
    )
