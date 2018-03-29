from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator


class ObjectWithSymbolReferencesAndValidation(ObjectWithTypedSymbolReferences):
    @property
    def validator(self) -> PreOrPostSdsValidator:
        raise NotImplementedError('abstract method')
