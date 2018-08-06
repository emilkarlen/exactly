from pathlib import Path
from typing import Optional, List

from exactly_lib.common.err_msg import rendering
from exactly_lib.common.err_msg import source_location
from exactly_lib.common.err_msg.definitions import Blocks, single_str_block
from exactly_lib.definitions import type_system
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.data.value_restriction import ValueRestrictionFailure
from exactly_lib.symbol.err_msg.error_message_format import source_lines
from exactly_lib.symbol.resolver_structure import SymbolContainer, SymbolValueResolver
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.line_source import LineSequence

_WHICH_IS_A_BUILTIN_SYMBOL = 'which is a builtin symbol'

_IS_A_BUILTIN_SYMBOL = 'is a builtin symbol'


def _is_a_builtin_symbol(symbol_name: str) -> str:
    return symbol_name + ' ' + _IS_A_BUILTIN_SYMBOL


def invalid_type_msg(expected_value_types: List[ValueType],
                     symbol_name: str,
                     container_of_actual: SymbolContainer) -> ValueRestrictionFailure:
    actual = container_of_actual.resolver
    if not isinstance(actual, SymbolValueResolver):
        raise TypeError('Symbol table contains a value that is not a {}: {}'.format(
            type(SymbolValueResolver),
            str(actual)
        ))
    assert isinstance(actual, SymbolValueResolver)  # Type info for IDE
    header_lines = invalid_type_header_lines(expected_value_types,
                                             actual.value_type,
                                             symbol_name,
                                             container_of_actual)
    how_to_fix_lines = invalid_type_how_to_fix_lines(expected_value_types)
    return ValueRestrictionFailure('\n'.join(header_lines),
                                   how_to_fix='\n'.join(how_to_fix_lines))


def invalid_type_header_lines(expected: List[ValueType],
                              actual: ValueType,
                              symbol_name: str,
                              container: SymbolContainer) -> List[str]:
    def expected_type_str() -> str:
        if len(expected) == 1:
            return _type_name_of(expected[0])
        else:
            return 'One of ' + (', '.join(map(_type_name_of, expected)))

    ret_val = ([
                   'Illegal type, of symbol "{}"'.format(symbol_name)
               ] +
               defined_at_line__err_msg_lines(container.source_location) +
               [
                   '',
                   'Found    : ' + _type_name_of(actual),
                   'Expected : ' + expected_type_str(),
               ])
    return ret_val


def invalid_type_how_to_fix_lines(expected_value_types: list) -> List[str]:
    from exactly_lib.definitions.test_case.instructions import define_symbol
    from exactly_lib.definitions.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
    from exactly_lib.definitions.formatting import InstructionName
    from exactly_lib.definitions.message_rendering import render_paragraph_item

    def_name_emphasised = InstructionName(SYMBOL_DEFINITION_INSTRUCTION_NAME).emphasis

    header = [
        'Define a legal symbol using the {} instruction:'.format(def_name_emphasised),
        '',
    ]

    def_instruction_syntax_table = define_symbol.def_syntax_table(expected_value_types)

    return header + render_paragraph_item(def_instruction_syntax_table)


def _type_name_of(value_type: ValueType) -> str:
    return type_system.TYPE_INFO_DICT[value_type].identifier


def duplicate_symbol_definition(already_defined_symbol: Optional[SourceLocationInfo],
                                name: str) -> str:
    header_block = [
        'Symbol `{}\' has already been defined:'.format(name)
    ]
    def_src_blocks = (
        [[_is_a_builtin_symbol(name)]]
        if already_defined_symbol is None
        else _definition_source_blocks(already_defined_symbol)
    )
    blocks = [header_block] + def_src_blocks

    return rendering.blocks_as_str(blocks)


def undefined_symbol(reference: su.SymbolReference) -> str:
    from exactly_lib.definitions.formatting import InstructionName
    from exactly_lib.definitions.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
    def_name_emphasised = InstructionName(SYMBOL_DEFINITION_INSTRUCTION_NAME).emphasis
    lines = [
        'Symbol `{}\' is undefined.'.format(reference.name),
        '',
        'Define a symbol using the {} instruction.'.format(def_name_emphasised),
    ]
    return '\n'.join(lines)


def defined_at_line__err_msg_lines(definition_source: Optional[SourceLocationInfo]) -> List[str]:
    if definition_source is None:
        return [_WHICH_IS_A_BUILTIN_SYMBOL]
    else:
        blocks = [['defined at']] + _definition_source_blocks(definition_source)
        return rendering.blocks_as_lines(blocks)


def _definition_source_blocks(definition_source: SourceLocationInfo) -> Blocks:
    formatter = source_location.default_formatter()
    return formatter.source_location_path(Path('.'),
                                          definition_source.source_location_path)


def _builtin_or_user_defined_source_blocks(definition_source: Optional[SourceLocationInfo]) -> Blocks:
    if definition_source is None:
        return [
            single_str_block(_WHICH_IS_A_BUILTIN_SYMBOL)
        ]
    else:
        formatter = source_location.default_formatter()
        return formatter.source_location_path(Path('.'),
                                              definition_source.source_location_path)


def source_line_of_symbol(definition_source: LineSequence) -> str:
    if definition_source is None:
        return _WHICH_IS_A_BUILTIN_SYMBOL
    else:
        return source_lines(definition_source)
