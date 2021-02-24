import unittest

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources import source_location_assertions as asrt_src_loc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.any_sdv_assertions import equals_data_type_sdv
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


def equals_container(expected: SymbolContainer,
                     ignore_source_line: bool = True) -> Assertion[SymbolContainer]:
    """
    :param expected: Must contain a data type value
    """

    component_assertions = [
        asrt.sub_component('value_type',
                           SymbolContainer.value_type.fget,
                           asrt.is_(expected.value_type)),
    ]

    if not ignore_source_line:
        component_assertions.append(
            asrt.sub_component(
                'definition_source',
                SymbolContainer.definition_source.fget,
                equals_line_sequence(expected.definition_source)
            )
        )
    component_assertions.append(
        asrt.sub_component(
            'source_location',
            SymbolContainer.source_location.fget,
            asrt.is_none_or_instance_with(
                SourceLocationInfo,
                asrt_src_loc.is_valid_source_location_info())
        ),

    )

    expected_sdv = expected.sdv
    assert isinstance(expected_sdv, DataTypeSdv), 'All actual values must be DataTypeSdv'
    component_assertions.append(asrt.sub_component('sdv',
                                                   SymbolContainer.sdv.fget,
                                                   equals_data_type_sdv(expected_sdv)))
    return asrt.is_instance_with(SymbolContainer,
                                 asrt.and_(component_assertions))


def equals_symbol_table(expected: SymbolTable,
                        ignore_source_line: bool = True) -> Assertion[SymbolTable]:
    """
    :param expected: Must contain only data type values
    """
    return _EqualsSymbolTable(expected, ignore_source_line)


class _EqualsSymbolTable(AssertionBase[SymbolTable]):
    def __init__(self,
                 expected: SymbolTable,
                 ignore_source_line: bool = True
                 ):
        self.ignore_source_line = ignore_source_line
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, SymbolTable)
        assert isinstance(value, SymbolTable)
        put.assertEqual(self.expected.names_set,
                        value.names_set,
                        message_builder.apply('names in symbol table'))
        for name in self.expected.names_set:
            actual_value = value.lookup(name)

            put.assertIsInstance(actual_value, SymbolContainer,
                                 message_builder.apply('actual container for ' + name))
            assert isinstance(actual_value, SymbolContainer)

            expected_container = self.expected.lookup(name)

            put.assertIsInstance(expected_container, SymbolContainer,
                                 message_builder.apply('expected container for ' + name))
            assert isinstance(expected_container, SymbolContainer)

            equals_container(expected_container).apply(
                put,
                actual_value,
                message_builder.for_sub_component('Value of symbol ' + name)
            )
