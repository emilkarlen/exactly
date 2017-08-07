from exactly_lib.execution.error_message_format import defined_at_line__err_msg_lines
from exactly_lib.help_texts import message_rendering
from exactly_lib.symbol.resolver_structure import ResolverContainer, SymbolValueResolver
from exactly_lib.symbol.restriction import ValueRestrictionFailure
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, SpecificPathRelativity, \
    RelOptionType
from exactly_lib.type_system_values.value_type import ValueType


def invalid_type_msg(expected: ValueType,
                     symbol_name: str,
                     container_of_actual: ResolverContainer) -> ValueRestrictionFailure:
    actual = container_of_actual.resolver
    if not isinstance(actual, SymbolValueResolver):
        raise TypeError('Symbol table contains a value that is not a {}: {}'.format(
            type(SymbolValueResolver),
            str(actual)
        ))
    assert isinstance(actual, SymbolValueResolver)  # Type info for IDE
    header_lines = invalid_type_header_lines(expected,
                                             actual.value_type,
                                             symbol_name,
                                             container_of_actual)
    how_to_fix_lines = invalid_type_how_to_fix_lines(expected)
    return ValueRestrictionFailure('\n'.join(header_lines),
                                   how_to_fix='\n'.join(how_to_fix_lines))


def unsatisfied_path_relativity(symbol_name: str,
                                container: ResolverContainer,
                                accepted: PathRelativityVariants,
                                actual_relativity: SpecificPathRelativity) -> str:
    from exactly_lib.help_texts.test_case.instructions import assign_symbol as help_texts
    from exactly_lib.help_texts import file_ref as file_ref_texts
    from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
    from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

    def option_description_row(rel_opt: RelOptionType) -> list:
        rel_option_info = REL_OPTIONS_MAP[rel_opt]
        return [rel_option_info.description,
                '(' + long_option_syntax(rel_option_info.option_name.long) + ')']

    def option_description(rel_opt: RelOptionType) -> str:
        rel_option_info = REL_OPTIONS_MAP[rel_opt]
        return '{} ({})'.format(rel_option_info.description,
                                long_option_syntax(rel_option_info.option_name.long))

    def _render_actual_relativity() -> str:
        if actual_relativity.is_absolute:
            return file_ref_texts.RELATIVITY_DESCRIPTION_ABSOLUTE
        return option_description(actual_relativity.relativity_type)

    def _accepted_relativities_table_rows() -> list:
        rows = []
        if accepted.absolute:
            rows.append([file_ref_texts.RELATIVITY_DESCRIPTION_ABSOLUTE])
        for rel_opt in accepted.rel_option_types:
            rows.append(option_description_row(rel_opt))
        return rows

    lines = ([
                 'Illegal relativity, of {} symbol "{}"'.format(help_texts.TYPE_INFO_DICT[ValueType.PATH].type_name,
                                                                symbol_name)
             ] +
             defined_at_line__err_msg_lines(container.definition_source) +
             [
                 '',
                 'Found    : ' + _render_actual_relativity(),
                 'Expected : ',
             ])
    accepted_relativities_table_rows = _accepted_relativities_table_rows()
    table_lines = message_rendering.render_single_text_cell_table_to_lines(accepted_relativities_table_rows,
                                                                           indent='     ')

    lines.extend(table_lines)
    return '\n'.join(lines)


def invalid_type_header_lines(expected: ValueType,
                              actual: ValueType,
                              symbol_name: str,
                              container: ResolverContainer) -> list:
    from exactly_lib.help_texts.test_case.instructions import assign_symbol as help_texts
    ret_val = ([
                   'Illegal type, of symbol "{}"'.format(symbol_name)
               ] +
               defined_at_line__err_msg_lines(container.definition_source) +
               [
                   '',
                   'Found    : ' + help_texts.TYPE_INFO_DICT[actual].type_name,
                   'Expected : ' + help_texts.TYPE_INFO_DICT[expected].type_name,
               ])
    return ret_val


def invalid_type_how_to_fix_lines(expected: ValueType) -> list:
    from exactly_lib.help_texts.test_case.instructions import assign_symbol as help_texts
    from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
    from exactly_lib.help_texts.names.formatting import InstructionName
    def_name_emphasised = InstructionName(SYMBOL_DEFINITION_INSTRUCTION_NAME).emphasis
    ret_val = [
        'Define a {} symbol using the {} instruction:'.format(help_texts.TYPE_INFO_DICT[expected].type_name,
                                                              def_name_emphasised),
        '',
    ]
    def_instruction_syntax_list = [
        SYMBOL_DEFINITION_INSTRUCTION_NAME + ' ' + syntax
        for syntax in help_texts.TYPE_INFO_DICT[expected].def_instruction_syntax_lines_function()
    ]
    ret_val.extend(def_instruction_syntax_list)
    return ret_val
