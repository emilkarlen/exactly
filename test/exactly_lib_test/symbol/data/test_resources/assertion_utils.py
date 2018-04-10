from typing import Sequence

from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.data import file_ref_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.restrictions import value_restrictions as vr
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.string_resolvers import str_constant
from exactly_lib.symbol.data.value_restriction import ValueRestriction
from exactly_lib.symbol.resolver_structure import SymbolContainer, DataValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl


def symbol_table_with_values_matching_references(references: Sequence[SymbolReference]) -> SymbolTable:
    value_constructor = _ValueCorrespondingToValueRestriction()
    elements = {}
    for ref in references:
        assert isinstance(ref, su.SymbolReference), "Informs IDE of type"
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
    return file_ref_resolvers.constant(file_ref_test_impl('file_ref_test_impl', relativity))


class _ValueCorrespondingToValueRestriction(vr.ValueRestrictionVisitor):
    def visit_none(self, x: vr.AnyDataTypeRestriction) -> DataValueResolver:
        return str_constant('a string (from <no restriction>)')

    def visit_string(self, x: vr.StringRestriction) -> DataValueResolver:
        return str_constant('a string (from <string value restriction>)')

    def visit_file_ref_relativity(self, x: vr.FileRefRelativityRestriction) -> DataValueResolver:
        return file_ref_resolver_test_impl(x.accepted)


def _resolver_container(value: FileRefResolver) -> SymbolContainer:
    return SymbolContainer(value,
                           single_line_sequence(1, 'source line'))
