from exactly_lib.named_element.resolver_structure import FileSelectorResolver
from exactly_lib.type_system.file_selector import FileSelector
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.named_element.test_resources import resolver_structure_assertions as asrt_ne
from exactly_lib_test.named_element.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class FileSelectorResolverConstantTestImpl(FileSelectorResolver):
    def __init__(self, resolved_value: FileSelector,
                 references: list = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> FileSelector:
        return self._resolved_value

    @property
    def references(self) -> list:
        return self._references

    def resolve(self, named_elements: SymbolTable) -> FileSelector:
        return self._resolved_value


IS_FILE_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.FILE_SELECTOR)


def is_file_selector_reference_to(name_of_file_selector: str) -> asrt.ValueAssertion:
    return asrt_ne.matches_reference(asrt.equals(name_of_file_selector),
                                     IS_FILE_REFERENCE_RESTRICTION)
