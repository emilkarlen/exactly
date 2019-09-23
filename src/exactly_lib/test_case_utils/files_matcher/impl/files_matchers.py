from abc import ABC
from typing import Callable

from exactly_lib.symbol.logic.files_matcher import FilesMatcherConstructor, FilesMatcher
from exactly_lib.symbol.logic.files_matcher import FilesMatcherResolver
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.util.file_utils import TmpDirFileSpace


class ConstantConstructor(FilesMatcherConstructor):
    def __init__(self, constant: FilesMatcher):
        self._constant = constant

    def construct(self, tmp_files_space: TmpDirFileSpace) -> FilesMatcher:
        return self._constant


class ConstructorFromFunction(FilesMatcherConstructor):
    def __init__(self, constructor: Callable[[TmpDirFileSpace], FilesMatcher]):
        self._constructor = constructor

    def construct(self, tmp_files_space: TmpDirFileSpace) -> FilesMatcher:
        return self._constructor(tmp_files_space)


class FilesMatcherResolverBase(FilesMatcherResolver, ABC):
    def __init__(self,
                 validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator(),
                 ):
        self._validator = validator

    def validator(self) -> PreOrPostSdsValidator:
        return self._validator
