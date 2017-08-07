from exactly_lib.execution.error_message_format import defined_at_line__err_msg_lines
from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.symbol.resolver_structure import ResolverContainer, SymbolValueResolver
from exactly_lib.symbol.restriction import ValueRestriction, ValueRestrictionFailure
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, SpecificPathRelativity, \
    RelOptionType
from exactly_lib.test_case_file_structure.relativity_validation import is_satisfied_by
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class NoRestriction(ValueRestriction):
    """
    No restriction - a restriction that any value satisfies.
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: ResolverContainer) -> str:
        return None


class StringRestriction(ValueRestriction):
    """
    Restriction to string values.
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: ResolverContainer) -> ValueRestrictionFailure:
        if not isinstance(container.resolver, StringResolver):
            return _invalid_type_msg(ValueType.STRING, symbol_name, container)
        return None


class FileRefRelativityRestriction(ValueRestriction):
    """
    Restricts to `FileRefValue` and `PathRelativityVariants`
    """

    def __init__(self, accepted: PathRelativityVariants):
        self._accepted = accepted

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: ResolverContainer) -> ValueRestrictionFailure:
        resolver = container.resolver
        if not isinstance(resolver, FileRefResolver):
            return _invalid_type_msg(ValueType.PATH, symbol_name, container)
        file_ref = resolver.resolve(symbol_table)
        actual_relativity = file_ref.relativity()
        satisfaction = is_satisfied_by(actual_relativity, self._accepted)
        if satisfaction:
            return None
        else:
            msg = _unsatisfied_path_relativity(symbol_name, container, self._accepted, actual_relativity)
            return ValueRestrictionFailure(msg)

    @property
    def accepted(self) -> PathRelativityVariants:
        return self._accepted


class ValueRestrictionVisitor:
    def visit(self, x: ValueRestriction):
        if isinstance(x, NoRestriction):
            return self.visit_none(x)
        if isinstance(x, StringRestriction):
            return self.visit_string(x)
        if isinstance(x, FileRefRelativityRestriction):
            return self.visit_file_ref_relativity(x)
        raise TypeError('%s is not an instance of %s' % (str(x), str(ValueRestriction)))

    def visit_none(self, x: NoRestriction):
        raise NotImplementedError()

    def visit_string(self, x: StringRestriction):
        raise NotImplementedError()

    def visit_file_ref_relativity(self, x: FileRefRelativityRestriction):
        raise NotImplementedError()


def _invalid_type_msg(expected: ValueType,
                      symbol_name: str,
                      container_of_actual: ResolverContainer) -> ValueRestrictionFailure:
    actual = container_of_actual.resolver
    if not isinstance(actual, SymbolValueResolver):
        raise TypeError('Symbol table contains a value that is not a {}: {}'.format(
            type(SymbolValueResolver),
            str(actual)
        ))
    assert isinstance(actual, SymbolValueResolver)  # Type info for IDE
    header_lines = _invalid_type_header_lines(expected,
                                              actual.value_type,
                                              symbol_name,
                                              container_of_actual)
    how_to_fix_lines = _invalid_type_how_to_fix_lines(expected)
    return ValueRestrictionFailure('\n'.join(header_lines),
                                   how_to_fix='\n'.join(how_to_fix_lines))


def _unsatisfied_path_relativity(symbol_name: str,
                                 container: ResolverContainer,
                                 accepted: PathRelativityVariants,
                                 actual_relativity: SpecificPathRelativity) -> str:
    from exactly_lib.help_texts.test_case.instructions import assign_symbol as help_texts
    from exactly_lib.help_texts import file_ref as file_ref_texts
    from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
    from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

    def option_description(rel_opt: RelOptionType) -> str:
        rel_option_info = REL_OPTIONS_MAP[rel_opt]
        return '{} ({})'.format(rel_option_info.description,
                                long_option_syntax(rel_option_info.option_name.long))

    def _render_actual_relativity() -> str:
        if actual_relativity.is_absolute:
            return file_ref_texts.RELATIVITY_DESCRIPTION_ABSOLUTE
        return option_description(actual_relativity.relativity_type)

    def _legal_relativities_lines() -> list:
        ret_val = []
        header = '     '
        if accepted.absolute:
            ret_val.append(header + file_ref_texts.RELATIVITY_DESCRIPTION_ABSOLUTE)
        for rel_opt in accepted.rel_option_types:
            ret_val.append(header + option_description(rel_opt))

        return ret_val

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
    lines.extend(_legal_relativities_lines())
    return '\n'.join(lines)


def _invalid_type_header_lines(expected: ValueType,
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


def _invalid_type_how_to_fix_lines(expected: ValueType) -> list:
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
