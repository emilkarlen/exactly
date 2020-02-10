from abc import ABC

from exactly_lib.symbol.sdv_structure import ObjectWithSymbolReferences
from exactly_lib.test_case.validation.sdv_validation import SdvValidator


class WithValidation:
    @property
    def validator(self) -> SdvValidator:
        raise NotImplementedError('abstract method')


class ObjectWithSymbolReferencesAndValidation(ObjectWithSymbolReferences, WithValidation, ABC):
    pass
