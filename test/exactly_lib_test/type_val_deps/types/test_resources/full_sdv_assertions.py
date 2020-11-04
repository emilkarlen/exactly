from typing import Type, Sequence

from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_sdv_attributes(type_: Type[FullDepsSdv],
                           references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                           ) -> ValueAssertion[FullDepsSdv]:
    return asrt.is_instance_with(
        type_,
        asrt.sub_component(
            'references',
            sdv_structure.get_references,
            references),
    )
