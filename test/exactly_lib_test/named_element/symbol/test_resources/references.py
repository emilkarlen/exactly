from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.symbol.restrictions import reference_restrictions


def reference_to_any_data_type_value(symbol_name: str) -> NamedElementReference:
    return NamedElementReference(symbol_name,
                                 reference_restrictions.is_any_data_type())
