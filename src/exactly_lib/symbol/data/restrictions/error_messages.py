from exactly_lib.help_texts import message_rendering
from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, SpecificPathRelativity, \
    RelOptionType
from exactly_lib.type_system.value_type import DataValueType
from exactly_lib.util.error_message_format import defined_at_line__err_msg_lines


def unsatisfied_path_relativity(symbol_name: str,
                                container: SymbolContainer,
                                accepted: PathRelativityVariants,
                                actual_relativity: SpecificPathRelativity) -> str:
    from exactly_lib.help_texts import file_ref
    from exactly_lib.help_texts.test_case.instructions import define_symbol
    from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
    from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

    def option_description_row(rel_opt: RelOptionType) -> list:
        rel_option_info = REL_OPTIONS_MAP[rel_opt]
        return [rel_option_info.informative_name,
                '(' + long_option_syntax(rel_option_info.option_name.long) + ')']

    def option_description(rel_opt: RelOptionType) -> str:
        rel_option_info = REL_OPTIONS_MAP[rel_opt]
        return '{} ({})'.format(rel_option_info.informative_name,
                                long_option_syntax(rel_option_info.option_name.long))

    def _render_actual_relativity() -> str:
        if actual_relativity.is_absolute:
            return file_ref.RELATIVITY_DESCRIPTION_ABSOLUTE
        return option_description(actual_relativity.relativity_type)

    def _accepted_relativities_table_rows() -> list:
        rows = []
        if accepted.absolute:
            rows.append([file_ref.RELATIVITY_DESCRIPTION_ABSOLUTE])
        for rel_opt in accepted.rel_option_types:
            rows.append(option_description_row(rel_opt))
        return rows

    lines = ([
                 'Illegal relativity, of {} symbol "{}"'.format(
                     define_symbol.DATA_TYPE_INFO_DICT[DataValueType.PATH].identifier,
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
