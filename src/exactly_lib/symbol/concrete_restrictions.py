from exactly_lib.symbol.concrete_values import FileRefResolver
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.symbol.value_restriction import ValueRestriction, ReferenceRestrictions, FailureInfo
from exactly_lib.symbol.value_structure import ValueContainer, ValueType, SymbolValueResolver
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, SpecificPathRelativity, \
    RelOptionType
from exactly_lib.test_case_file_structure.relativity_validation import is_satisfied_by
from exactly_lib.util.symbol_table import SymbolTable


class NoRestriction(ValueRestriction):
    """
    No restriction - a restriction that any value satisfies.
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: ValueContainer) -> str:
        return None


class StringRestriction(ValueRestriction):
    """
    Restriction to string values.
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value_container: ValueContainer) -> str:
        if not isinstance(value_container.value, StringResolver):
            return _invalid_type_msg(ValueType.STRING, symbol_name, value_container)
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
                        value_container: ValueContainer) -> str:
        value = value_container.value
        if not isinstance(value, FileRefResolver):
            return _invalid_type_msg(ValueType.PATH, symbol_name, value_container)
        file_ref = value.resolve(symbol_table)
        actual_relativity = file_ref.relativity()
        satisfaction = is_satisfied_by(actual_relativity, self._accepted)
        if satisfaction:
            return None
        else:
            return _unsatisfied_path_relativity(symbol_name,
                                                value_container,
                                                self._accepted,
                                                actual_relativity,
                                                )

    @property
    def accepted(self) -> PathRelativityVariants:
        return self._accepted


class EitherStringOrFileRefRelativityRestriction(ValueRestriction):
    """
    Restricts to Either a `StringRestriction` or a `FileRefRelativityRestriction`

    This could be designed a generic OR restriction.  This, less flexible solution,
    has been selected (for the moment) because of simplicity.
    """

    def __init__(self,
                 string_restriction: StringRestriction,
                 file_ref_restriction: FileRefRelativityRestriction):
        self._string_restriction = string_restriction
        self._file_ref_restriction = file_ref_restriction

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value_container: ValueContainer) -> str:
        value = value_container.value
        if isinstance(value, StringResolver):
            return self.string_restriction.is_satisfied_by(symbol_table, symbol_name, value_container)
        elif isinstance(value, FileRefResolver):
            return self.file_ref_restriction.is_satisfied_by(symbol_table, symbol_name, value_container)

    @property
    def string_restriction(self) -> StringRestriction:
        return self._string_restriction

    @property
    def file_ref_restriction(self) -> FileRefRelativityRestriction:
        return self._file_ref_restriction


class ValueRestrictionVisitor:
    def visit(self, x: ValueRestriction):
        if isinstance(x, NoRestriction):
            return self.visit_none(x)
        if isinstance(x, StringRestriction):
            return self.visit_string(x)
        if isinstance(x, FileRefRelativityRestriction):
            return self.visit_file_ref_relativity(x)
        if isinstance(x, EitherStringOrFileRefRelativityRestriction):
            return self.visit_string_or_file_ref_relativity(x)
        raise TypeError('%s is not an instance of %s' % (str(x), str(ValueRestriction)))

    def visit_none(self, x: NoRestriction):
        raise NotImplementedError()

    def visit_string(self, x: StringRestriction):
        raise NotImplementedError()

    def visit_file_ref_relativity(self, x: FileRefRelativityRestriction):
        raise NotImplementedError()

    def visit_string_or_file_ref_relativity(self, x: EitherStringOrFileRefRelativityRestriction):
        raise NotImplementedError()


class FailureOfDirectReference(FailureInfo):
    def __init__(self, error_message: str):
        self._error_message = error_message

    @property
    def error_message(self) -> str:
        return self._error_message


class FailureOfIndirectReference(FailureInfo):
    def __init__(self,
                 failing_symbol: str,
                 path_to_failing_symbol: list,
                 error_message: str):
        self._failing_symbol = failing_symbol
        self._path_to_failing_symbol = path_to_failing_symbol
        self._error_message = error_message

    @property
    def failing_symbol(self) -> str:
        """
        The name of the symbol that causes the failure
        """
        return self._failing_symbol

    @property
    def path_to_failing_symbol(self) -> list:
        """
        The references (from top to bottom) that leads to the failing symbol
        """
        return self._path_to_failing_symbol

    @property
    def error_message(self) -> str:
        return self._error_message


class ReferenceRestrictionsOnDirectAndIndirect(ReferenceRestrictions):
    """
    Restriction with one `ValueRestriction` that is applied on the
    directly referenced symbol; and another that (if it is not None) is applied on every indirectly
    referenced symbol.
    """

    def __init__(self,
                 direct: ValueRestriction,
                 indirect: ValueRestriction = None):
        self._direct = direct
        self._indirect = indirect

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: ValueContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param value: The value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        result = self._direct.is_satisfied_by(symbol_table, symbol_name, value)
        if result is not None:
            return FailureOfDirectReference(result)
        if self._indirect is None:
            return None
        return self.check_indirect(symbol_table, value.value.references)

    @property
    def direct(self) -> ValueRestriction:
        """
        Restriction on the symbol that is the direct target of the reference.
        """
        return self._direct

    @property
    def indirect(self) -> ValueRestriction:
        """
        Restriction that must be satisfied by the symbols references indirectly referenced.
        :rtype: None or ValueRestriction
        """
        return self._indirect

    def check_indirect(self,
                       symbol_table: SymbolTable,
                       references: list) -> FailureOfIndirectReference:
        for reference in references:
            symbol_value = symbol_table.lookup(reference.name)
            result = self._indirect.is_satisfied_by(symbol_table, reference.name, symbol_value)
            if result is not None:
                return FailureOfIndirectReference(result)
            result = self.check_indirect(symbol_table, symbol_value.value.references)
            if result is not None:
                return result
        return None


class OrReferenceRestrictions(ReferenceRestrictions):
    def __init__(self, simple_reference_restriction_parts: list):
        self._parts = tuple(simple_reference_restriction_parts)

    @property
    def parts(self) -> tuple:
        return self._parts

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: ValueContainer) -> FailureInfo:
        for restriction_on_direct_and_indirect in self._parts:
            assert isinstance(restriction_on_direct_and_indirect, ReferenceRestrictionsOnDirectAndIndirect)
            on_direct = restriction_on_direct_and_indirect.direct.is_satisfied_by(symbol_table, symbol_name, value)
            if on_direct is None:
                if restriction_on_direct_and_indirect.indirect is None:
                    return None
                else:
                    return restriction_on_direct_and_indirect.check_indirect(symbol_table,
                                                                             value.value.references)
        return FailureOfDirectReference('OR: no restriction is satisfied. TODO: improve error message')


class PathOrStringReferenceRestrictions(ReferenceRestrictions):
    def __init__(self, accepted_relativities: PathRelativityVariants):
        self._accepted_relativities = accepted_relativities

    @property
    def accepted_relativities(self) -> PathRelativityVariants:
        return self._accepted_relativities

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: ValueContainer) -> str:
        raise NotImplementedError('TODO')


def _invalid_type_msg(expected: ValueType,
                      symbol_name: str,
                      container_of_actual: ValueContainer) -> str:
    actual = container_of_actual.value
    if not isinstance(actual, SymbolValueResolver):
        raise TypeError('Symbol table contains a value that is not a {}: {}'.format(
            type(SymbolValueResolver),
            str(actual)
        ))
    assert isinstance(actual, SymbolValueResolver)  # Type info for IDE
    lines = _invalid_type_header_lines(expected,
                                       actual.value_type,
                                       symbol_name,
                                       container_of_actual)
    return '\n'.join(lines)


class ReferenceRestrictionsVisitor:
    def visit(self, x: ReferenceRestrictions):
        if isinstance(x, ReferenceRestrictionsOnDirectAndIndirect):
            return self.visit_direct_and_indirect(x)
        if isinstance(x, PathOrStringReferenceRestrictions):
            return self.visit_path_or_string(x)
        if isinstance(x, OrReferenceRestrictions):
            return self.visit_or(x)
        raise TypeError('%s is not an instance of %s' % (str(x), str(ReferenceRestrictions)))

    def visit_direct_and_indirect(self, x: ReferenceRestrictionsOnDirectAndIndirect):
        raise NotImplementedError()

    def visit_path_or_string(self, x: PathOrStringReferenceRestrictions):
        raise NotImplementedError()

    def visit_or(self, x: OrReferenceRestrictions):
        raise NotImplementedError()


def _unsatisfied_path_relativity(symbol_name: str,
                                 value_container: ValueContainer,
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

    def _accepted_relativities_lines() -> list:
        ret_val = []
        header = '   '
        if accepted.absolute:
            ret_val.append(header + file_ref_texts.RELATIVITY_DESCRIPTION_ABSOLUTE)
        for rel_opt in accepted.rel_option_types:
            ret_val.append(header + option_description(rel_opt))

        return ret_val

    lines = [
        'Unaccepted relativity, of {} symbol "{}"'.format(help_texts.TYPE_INFO_DICT[ValueType.PATH].type_name,
                                                          symbol_name),
        'defined at line {}: {}'.format(value_container.definition_source.line_number,
                                        value_container.definition_source.text),
        '',
        'Found    : ' + _render_actual_relativity(),
        'Accepted : ',
    ]
    lines.extend(_accepted_relativities_lines())
    return '\n'.join(lines)


def _invalid_type_header_lines(expected: ValueType,
                               actual: ValueType,
                               symbol_name: str,
                               value_container: ValueContainer) -> list:
    from exactly_lib.help_texts.test_case.instructions import assign_symbol as help_texts
    from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
    from exactly_lib.help_texts.names.formatting import InstructionName
    def_name_emphasised = InstructionName(SYMBOL_DEFINITION_INSTRUCTION_NAME).emphasis
    ret_val = [
        'Invalid type, of symbol "{}"'.format(symbol_name),
        'defined at line {}: {}'.format(value_container.definition_source.line_number,
                                        value_container.definition_source.text),
        '',
        'Expected : ' + help_texts.TYPE_INFO_DICT[expected].type_name,
        'Found    : ' + help_texts.TYPE_INFO_DICT[actual].type_name,
        '',
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
