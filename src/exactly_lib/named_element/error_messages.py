from exactly_lib.execution.error_message_format import defined_at_line__err_msg_lines
from exactly_lib.named_element.resolver_structure import NamedElementContainer, NamedElementResolver
from exactly_lib.named_element.symbol.value_restriction import ValueRestrictionFailure
from exactly_lib.type_system_values.value_type import ValueType


def invalid_type_msg(expected: ValueType,
                     symbol_name: str,
                     container_of_actual: NamedElementContainer) -> ValueRestrictionFailure:
    actual = container_of_actual.resolver
    if not isinstance(actual, NamedElementResolver):
        raise TypeError('Symbol table contains a value that is not a {}: {}'.format(
            type(NamedElementResolver),
            str(actual)
        ))
    assert isinstance(actual, NamedElementResolver)  # Type info for IDE
    header_lines = invalid_type_header_lines(expected,
                                             actual.value_type,
                                             symbol_name,
                                             container_of_actual)
    how_to_fix_lines = invalid_type_how_to_fix_lines(expected)
    return ValueRestrictionFailure('\n'.join(header_lines),
                                   how_to_fix='\n'.join(how_to_fix_lines))


def invalid_type_header_lines(expected: ValueType,
                              actual: ValueType,
                              symbol_name: str,
                              container: NamedElementContainer) -> list:
    from exactly_lib.help_texts import type_system
    ret_val = ([
                   'Illegal type, of symbol "{}"'.format(symbol_name)
               ] +
               defined_at_line__err_msg_lines(container.definition_source) +
               [
                   '',
                   'Found    : ' + type_system.TYPE_INFO_DICT[actual].type_name,
                   'Expected : ' + type_system.TYPE_INFO_DICT[expected].type_name,
               ])
    return ret_val


def invalid_type_how_to_fix_lines(expected: ValueType) -> list:
    from exactly_lib.help_texts.test_case.instructions import assign_symbol
    from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
    from exactly_lib.help_texts.names.formatting import InstructionName
    def_name_emphasised = InstructionName(SYMBOL_DEFINITION_INSTRUCTION_NAME).emphasis
    ret_val = [
        'Define a {} symbol using the {} instruction:'.format(assign_symbol.ANY_TYPE_INFO_DICT[expected].type_name,
                                                              def_name_emphasised),
        '',
    ]
    def_instruction_syntax_list = [
        SYMBOL_DEFINITION_INSTRUCTION_NAME + ' ' + syntax
        for syntax in assign_symbol.ANY_TYPE_INFO_DICT[expected].def_instruction_syntax_lines_function()
    ]
    ret_val.extend(def_instruction_syntax_list)
    return ret_val
