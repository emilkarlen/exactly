from abc import ABC
from typing import List, Callable

from exactly_lib.test_case.validation import ddv_validators
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_matcher.impl.ddv_base_class import FileMatcherDdvImplBase
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcher
from exactly_lib.type_system.logic.impls import combinator_matchers


class FileMatcherValueFromPrimitiveDdv(FileMatcherDdvImplBase):
    def __init__(self, primitive_value: FileMatcher):
        self._primitive_value = primitive_value

    def value_of_any_dependency(self, tcds: Tcds) -> FileMatcher:
        return self._primitive_value


class FileMatcherCompositionDdvBase(FileMatcherDdvImplBase, ABC):
    def __init__(self,
                 parts: List[FileMatcherDdv],
                 mk_primitive_value: Callable[[List[FileMatcher]], FileMatcher]):
        self._mk_primitive_value = mk_primitive_value
        self._parts = parts
        if not parts:
            raise ValueError('Composition must have at least one element')
        self._validator = ddv_validators.all_of([
            part.validator
            for part in parts
        ])

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> FileMatcher:
        return self._mk_primitive_value([
            part.value_of_any_dependency(tcds)
            for part in self._parts
        ])


class FileMatcherNotValue(FileMatcherCompositionDdvBase):
    def __init__(self, matcher: FileMatcherDdv):
        super().__init__([matcher],
                         lambda values: combinator_matchers.Negation(values[0]))


class FileMatcherAndValue(FileMatcherCompositionDdvBase):
    def __init__(self, parts: List[FileMatcherDdv]):
        super().__init__(parts,
                         lambda values: combinator_matchers.Conjunction(values))


class FileMatcherOrValue(FileMatcherCompositionDdvBase):
    def __init__(self, parts: List[FileMatcherDdv]):
        super().__init__(parts,
                         lambda values: combinator_matchers.Disjunction(values))


class FileMatcherDdvFromParts(FileMatcherDdvImplBase):
    def __init__(self,
                 validator: DdvValidator,
                 matcher: Callable[[Tcds], FileMatcher],
                 ):
        self._validator = validator
        self._matcher = matcher

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> FileMatcher:
        return self._matcher(tcds)
