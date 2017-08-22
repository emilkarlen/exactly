from exactly_lib.named_element import named_element_usage as su
from exactly_lib.named_element.resolver_structure import NamedValueContainer, SymbolValueResolver
from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.named_element.symbol.restrictions import value_restrictions as vr
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.named_element.symbol.string_resolver import string_constant
from exactly_lib.named_element.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.named_element.symbol.value_restriction import ValueRestriction
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl


def symbol_table_with_values_matching_references(references: list) -> SymbolTable:
    value_constructor = _ValueCorrespondingToValueRestriction()
    elements = {}
    for ref in references:
        assert isinstance(ref, su.NamedElementReference), "Informs IDE of type"
        restrictions = ref.restrictions
        assert isinstance(restrictions,
                          ReferenceRestrictionsOnDirectAndIndirect), 'Only handled/needed case for the moment'
        value_restriction = restrictions.direct
        assert isinstance(value_restriction, ValueRestriction)
        value = value_constructor.visit(value_restriction)
        elements[ref.name] = _resolver_container(value)
    return SymbolTable(elements)


def file_ref_resolver_test_impl(valid_relativities: PathRelativityVariants) -> FileRefResolver:
    relativity = list(valid_relativities.rel_option_types)[0]
    assert isinstance(relativity, RelOptionType)
    return FileRefConstant(file_ref_test_impl('file_ref_test_impl', relativity))


class _ValueCorrespondingToValueRestriction(vr.ValueRestrictionVisitor):
    def visit_none(self, x: vr.NoRestriction) -> SymbolValueResolver:
        return string_constant('a string (from <no restriction>)')

    def visit_string(self, x: vr.StringRestriction) -> SymbolValueResolver:
        return string_constant('a string (from <string value restriction>)')

    def visit_file_ref_relativity(self, x: vr.FileRefRelativityRestriction) -> SymbolValueResolver:
        return file_ref_resolver_test_impl(x.accepted)


def _resolver_container(value: FileRefResolver) -> NamedValueContainer:
    return NamedValueContainer(value, Line(1, 'source line'))
