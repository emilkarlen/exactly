from abc import ABC

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv, StringSourceAdv
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder


class StringSourceDdvTestImplBase(StringSourceDdv, ABC):
    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return StringSourceStructureBuilder(str(type(self)), ())


class StringSourceDdvWoResolvingTestImpl(StringSourceDdvTestImplBase):
    """A test impl StringSourceDdv that do not support resolving (to ADV)."""

    def __init__(self, validator: DdvValidator):
        self._validator = validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringSourceAdv:
        raise NotImplementedError('unsupported')

    @property
    def validator(self) -> DdvValidator:
        return self._validator
