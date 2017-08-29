from exactly_lib.named_element import resolver_structure
from exactly_lib.named_element.resolver_structure import LogicValueResolver, SymbolValueResolver
from exactly_lib.type_system_values.value_type import ElementType, ValueType, LogicValueType, SymbolValueType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_resolver_of_data_type(data_value_type: SymbolValueType,
                             value_type: ValueType) -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`NamedValueResolver`
    """

    return asrt.is_instance_with(SymbolValueResolver,
                                 asrt.and_([
                                     asrt.sub_component('element_type',
                                                        resolver_structure.get_element_type,
                                                        asrt.is_(ElementType.SYMBOL)),

                                     asrt.sub_component('data_value_type',
                                                        resolver_structure.get_data_value_type,
                                                        asrt.is_(data_value_type)),

                                     asrt.sub_component('value_type',
                                                        resolver_structure.get_value_type,
                                                        asrt.is_(value_type)),
                                 ]))


def is_resolver_of_logic_type(logic_value_type: LogicValueType,
                              value_type: ValueType) -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`NamedValueResolver`
    """

    return asrt.is_instance_with(LogicValueResolver,
                                 asrt.and_([
                                     asrt.sub_component('element_type',
                                                        resolver_structure.get_element_type,
                                                        asrt.is_(ElementType.LOGIC)),

                                     asrt.sub_component('logic_value_type',
                                                        resolver_structure.get_logic_value_type,
                                                        asrt.is_(logic_value_type)),

                                     asrt.sub_component('value_type',
                                                        resolver_structure.get_value_type,
                                                        asrt.is_(value_type)),
                                 ]))
