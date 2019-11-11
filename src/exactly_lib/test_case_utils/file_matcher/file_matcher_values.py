from abc import ABC
from typing import List, Callable

from exactly_lib.test_case.validation import pre_or_post_value_validators
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.file_matcher.impl.combinators import FileMatcherNot, FileMatcherAnd, FileMatcherOr
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue, FileMatcher


class FileMatcherValueFromPrimitiveValue(FileMatcherValue):
    def __init__(self, primitive_value: FileMatcher):
        self._primitive_value = primitive_value

    def value_of_any_dependency(self, tcds: HomeAndSds) -> FileMatcher:
        return self._primitive_value


class FileMatcherCompositionValueBase(FileMatcherValue, ABC):
    def __init__(self,
                 parts: List[FileMatcherValue],
                 mk_primitive_value: Callable[[List[FileMatcher]], FileMatcher]):
        self._mk_primitive_value = mk_primitive_value
        self._parts = parts
        if not parts:
            raise ValueError('Composition must have at least one element')
        self._validator = pre_or_post_value_validators.all_of([
            part.validator()
            for part in parts
        ])

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: HomeAndSds) -> FileMatcher:
        return self._mk_primitive_value([
            part.value_of_any_dependency(tcds)
            for part in self._parts
        ])


class FileMatcherNotValue(FileMatcherCompositionValueBase):
    def __init__(self, matcher: FileMatcherValue):
        super().__init__([matcher],
                         lambda values: FileMatcherNot(values[0]))


class FileMatcherAndValue(FileMatcherCompositionValueBase):
    def __init__(self, parts: List[FileMatcherValue]):
        super().__init__(parts,
                         lambda values: FileMatcherAnd(values))


class FileMatcherOrValue(FileMatcherCompositionValueBase):
    def __init__(self, parts: List[FileMatcherValue]):
        super().__init__(parts,
                         lambda values: FileMatcherOr(values))


class FileMatcherValueFromParts(FileMatcherValue):
    def __init__(self,
                 validator: PreOrPostSdsValueValidator,
                 matcher: Callable[[HomeAndSds], FileMatcher],
                 ):
        self._validator = validator
        self._matcher = matcher

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: HomeAndSds) -> FileMatcher:
        return self._matcher(tcds)
