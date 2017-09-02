from exactly_lib.help_texts import type_system
from exactly_lib.named_element.resolver_structure import NamedElementContainer, NamedElementResolver
from exactly_lib.named_element.symbol.value_restriction import ValueRestrictionFailure
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.error_message_format import defined_at_line__err_msg_lines


def invalid_type_msg(expected_value_types: list,
                     symbol_name: str,
                     container_of_actual: NamedElementContainer) -> ValueRestrictionFailure:
    actual = container_of_actual.resolver
    if not isinstance(actual, NamedElementResolver):
        raise TypeError('Symbol table contains a value that is not a {}: {}'.format(
            type(NamedElementResolver),
            str(actual)
        ))
    assert isinstance(actual, NamedElementResolver)  # Type info for IDE
    header_lines = invalid_type_header_lines(expected_value_types,
                                             actual.value_type,
                                             symbol_name,
                                             container_of_actual)
    how_to_fix_lines = invalid_type_how_to_fix_lines(expected_value_types)
    return ValueRestrictionFailure('\n'.join(header_lines),
                                   how_to_fix='\n'.join(how_to_fix_lines))


def invalid_type_header_lines(expected: list,
                              actual: ValueType,
                              symbol_name: str,
                              container: NamedElementContainer) -> list:
    def expected_type_str() -> str:
        if len(expected) == 1:
            return _type_name_of(expected[0])
        else:
            return 'One of ' + (', '.join(map(_type_name_of, expected)))

    ret_val = ([
                   'Illegal type, of symbol "{}"'.format(symbol_name)
               ] +
               defined_at_line__err_msg_lines(container.definition_source) +
               [
                   '',
                   'Found    : ' + _type_name_of(actual),
                   'Expected : ' + expected_type_str(),
               ])
    return ret_val


def invalid_type_how_to_fix_lines(expected_value_types: list) -> list:
    from exactly_lib.help_texts.test_case.instructions import assign_symbol
    from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
    from exactly_lib.help_texts.names.formatting import InstructionName
    def_name_emphasised = InstructionName(SYMBOL_DEFINITION_INSTRUCTION_NAME).emphasis
    ret_val = [
        'Define a legal symbol using the {} instruction:'.format(def_name_emphasised),
        '',
    ]

    def def_instruction_syntax_list_for_type(value_type: ValueType) -> list:
        return [
            SYMBOL_DEFINITION_INSTRUCTION_NAME + ' ' + syntax
            for syntax in assign_symbol.ANY_TYPE_INFO_DICT[value_type].def_instruction_syntax_lines_function()
        ]

    def_instruction_syntax_list = []
    for expected_type in expected_value_types:
        def_instruction_syntax_list.extend(def_instruction_syntax_list_for_type(expected_type))

    ret_val.extend(def_instruction_syntax_list)
    return ret_val


def _type_name_of(value_type: ValueType) -> str:
    return type_system.TYPE_INFO_DICT[value_type].type_name
