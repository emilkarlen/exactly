from pathlib import Path
from typing import Optional, List, Sequence

from exactly_lib.common.err_msg import rendering
from exactly_lib.common.err_msg import source_location
from exactly_lib.common.err_msg.definitions import Blocks, single_str_block
from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.common.report_rendering import block_text_docs
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.entity import all_entity_types, types
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference, \
    SymbolDependentValue
from exactly_lib.symbol.value_type import ValueType


def duplicate_symbol_definition(already_defined_symbol: Optional[SourceLocationInfo],
                                name: str) -> TextRenderer:
    return block_text_docs.major_blocks_of_string_blocks(
        _duplicate_symbol_definition(already_defined_symbol,
                                     name)
    )


def undefined_symbol(reference: SymbolReference) -> TextRenderer:
    return block_text_docs.major_blocks_of_string_blocks(
        _undefined_symbol(reference))


def invalid_type_msg(expected_value_types: Sequence[ValueType],
                     symbol_name: str,
                     container_of_actual: SymbolContainer) -> ErrorMessageWithFixTip:
    actual = container_of_actual.sdv
    if not isinstance(actual, SymbolDependentValue):
        raise TypeError('Symbol table contains a value that is not a {}: {}'.format(
            SymbolDependentValue,
            str(actual)
        ))
    assert isinstance(actual, SymbolDependentValue)  # Type info for IDE
    header_lines = _invalid_type_header_lines(expected_value_types,
                                              container_of_actual.value_type,
                                              symbol_name,
                                              container_of_actual)
    how_to_fix_lines = _invalid_type_how_to_fix_lines(expected_value_types)
    return ErrorMessageWithFixTip(
        text_docs.single_pre_formatted_line_object('\n'.join(header_lines)),
        how_to_fix=text_docs.single_pre_formatted_line_object('\n'.join(how_to_fix_lines))
    )


def defined_at_line__err_msg_lines(definition_source: Optional[SourceLocationInfo]) -> List[str]:
    if definition_source is None:
        return [_WHICH_IS_A_BUILTIN_SYMBOL]
    else:
        blocks = [['defined at']] + _definition_source_blocks(definition_source)
        return rendering.blocks_as_lines(blocks)


_WHICH_IS_A_BUILTIN_SYMBOL = 'which is ' + all_entity_types.BUILTIN_SYMBOL_ENTITY_TYPE_NAMES.name.singular_determined

_IS_A_BUILTIN_SYMBOL = 'is ' + all_entity_types.BUILTIN_SYMBOL_ENTITY_TYPE_NAMES.name.singular_determined


def _is_a_builtin_symbol(symbol_name: str) -> str:
    return symbol_name + ' ' + _IS_A_BUILTIN_SYMBOL


def _invalid_type_header_lines(expected: Sequence[ValueType],
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


def _invalid_type_how_to_fix_lines(expected_value_types: Sequence[ValueType]) -> List[str]:
    from exactly_lib.definitions.test_case.instructions import define_symbol
    from exactly_lib.definitions.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
    from exactly_lib.definitions.formatting import InstructionName
    from exactly_lib.definitions.message_rendering import render_paragraph_item

    def_name_emphasised = InstructionName(SYMBOL_DEFINITION_INSTRUCTION_NAME).emphasis

    header = [
        'Define a valid symbol using the {} instruction:'.format(def_name_emphasised),
        '',
    ]

    def_instruction_syntax_table = define_symbol.def_syntax_table(expected_value_types)

    return header + _indent_lines('  ', render_paragraph_item(def_instruction_syntax_table))


def _indent_lines(indent: str, lines: Sequence[str]) -> List[str]:
    return [
        indent + line
        for line in lines
    ]


def _type_name_of(value_type: ValueType) -> str:
    return types.VALUE_TYPE_2_TYPES_INFO_DICT[value_type].identifier


def _duplicate_symbol_definition(already_defined_symbol: Optional[SourceLocationInfo],
                                 name: str) -> Blocks:
    header_block = [
        'Symbol `{}\' has already been defined:'.format(name)
    ]
    def_src_blocks = (
        [[_is_a_builtin_symbol(name)]]
        if already_defined_symbol is None
        else _definition_source_blocks(already_defined_symbol)
    )
    return [header_block] + def_src_blocks


def _undefined_symbol(reference: SymbolReference) -> Blocks:
    from exactly_lib.definitions.formatting import InstructionName
    from exactly_lib.definitions.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
    def_name_emphasised = InstructionName(SYMBOL_DEFINITION_INSTRUCTION_NAME).emphasis
    return [
        ['Symbol `{}\' is undefined.'.format(reference.name)],
        ['Define a symbol using the {} instruction.'.format(def_name_emphasised)],
    ]


def _definition_source_blocks(definition_source: SourceLocationInfo) -> Blocks:
    formatter = source_location.default_formatter()
    return formatter.source_location_path(Path('.'),
                                          definition_source.source_location_path)


def builtin_or_user_defined_source_blocks(definition_source: Optional[SourceLocationInfo]) -> Blocks:
    if definition_source is None:
        return [
            single_str_block(_WHICH_IS_A_BUILTIN_SYMBOL)
        ]
    else:
        formatter = source_location.default_formatter()
        return formatter.source_location_path(Path('.'),
                                              definition_source.source_location_path)
