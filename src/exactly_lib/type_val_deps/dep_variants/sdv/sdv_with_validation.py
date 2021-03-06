from abc import ABC

from exactly_lib.symbol.sdv_structure import ObjectWithSymbolReferences
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator


class WithSdvValidation:
    @property
    def validator(self) -> SdvValidator:
        raise NotImplementedError('abstract method')


class ObjectWithSymbolReferencesAndSdvValidation(ObjectWithSymbolReferences, WithSdvValidation, ABC):
    pass
