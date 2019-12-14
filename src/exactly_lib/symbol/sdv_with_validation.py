from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.test_case.validation.sdv_validation import SdvValidator


class WithValidation:
    @property
    def validator(self) -> SdvValidator:
        raise NotImplementedError('abstract method')


class ObjectWithSymbolReferencesAndValidation(ObjectWithTypedSymbolReferences, WithValidation):
    pass
