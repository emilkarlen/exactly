import types

from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.symbol.resolver_structure import ResolverContainer, SymbolValueResolver
from exactly_lib.symbol.restriction import ValueRestriction, ReferenceRestrictions, FailureInfo, \
    ValueRestrictionFailure
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, SpecificPathRelativity, \
    RelOptionType
from exactly_lib.test_case_file_structure.relativity_validation import is_satisfied_by
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.error_message_format import defined_at_line__err_msg_lines
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
                        container: ResolverContainer) -> ValueRestrictionFailure:
        resolver = container.resolver
        if isinstance(resolver, StringResolver):
            return self.string_restriction.is_satisfied_by(symbol_table, symbol_name, container)
        elif isinstance(resolver, FileRefResolver):
            return self.file_ref_restriction.is_satisfied_by(symbol_table, symbol_name, container)

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
        raise TypeError('%s is not an instance of %s' % (str(x), str(ValueRestriction)))

    def visit_none(self, x: NoRestriction):
        raise NotImplementedError()

    def visit_string(self, x: StringRestriction):
        raise NotImplementedError()

    def visit_file_ref_relativity(self, x: FileRefRelativityRestriction):
        raise NotImplementedError()


class FailureOfDirectReference(FailureInfo):
    def __init__(self, error: ValueRestrictionFailure):
        self._error = error

    @property
    def error(self) -> ValueRestrictionFailure:
        return self._error


class FailureOfIndirectReference(FailureInfo):
    def __init__(self,
                 failing_symbol: str,
                 path_to_failing_symbol: list,
                 error: ValueRestrictionFailure,
                 meaning_of_failure: str = ''):
        self._failing_symbol = failing_symbol
        self._path_to_failing_symbol = path_to_failing_symbol
        self._error = error
        self._meaning_of_failure = meaning_of_failure

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
    def error(self) -> ValueRestrictionFailure:
        return self._error

    @property
    def meaning_of_failure(self) -> str:
        return self._meaning_of_failure


def no_restrictions() -> ReferenceRestrictions:
    """
    :return: A restriction that is unconditionally satisfied
    """
    return ReferenceRestrictionsOnDirectAndIndirect(NoRestriction())


class ReferenceRestrictionsOnDirectAndIndirect(ReferenceRestrictions):
    """
    Restriction with one `ValueRestriction` that is applied on the
    directly referenced symbol; and another that (if it is not None) is applied on every indirectly
    referenced symbol.
    """

    def __init__(self,
                 direct: ValueRestriction,
                 indirect: ValueRestriction = None,
                 meaning_of_failure_of_indirect_reference: str = ''):
        self._direct = direct
        self._indirect = indirect
        self._meaning_of_failure_of_indirect_reference = meaning_of_failure_of_indirect_reference

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: ResolverContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param value: The value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        result = self._direct.is_satisfied_by(symbol_table, symbol_name, container)
        if result is not None:
            return FailureOfDirectReference(result)
        if self._indirect is None:
            return None
        return self.check_indirect(symbol_table, container.resolver.references)

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

    @property
    def meaning_of_failure_of_indirect_reference(self) -> str:
        return self._meaning_of_failure_of_indirect_reference

    def check_indirect(self,
                       symbol_table: SymbolTable,
                       references: list) -> FailureOfIndirectReference:
        return self._check_indirect(symbol_table, (), references)

    def _check_indirect(self,
                        symbol_table: SymbolTable,
                        path_to_referring_symbol: tuple,
                        references: list) -> FailureOfIndirectReference:
        for reference in references:
            container = symbol_table.lookup(reference.name)
            result = self._indirect.is_satisfied_by(symbol_table, reference.name, container)
            if result is not None:
                return FailureOfIndirectReference(
                    failing_symbol=reference.name,
                    path_to_failing_symbol=list(path_to_referring_symbol),
                    error=result,
                    meaning_of_failure=self._meaning_of_failure_of_indirect_reference)
            result = self._check_indirect(symbol_table,
                                          path_to_referring_symbol + (reference.name,),
                                          container.resolver.references)
            if result is not None:
                return result
        return None


class OrRestrictionPart(tuple):
    def __new__(cls,
                selector: ValueType,
                restriction: ReferenceRestrictionsOnDirectAndIndirect):
        return tuple.__new__(cls, (selector, restriction))

    @property
    def selector(self) -> ValueType:
        return self[0]

    @property
    def restriction(self) -> ReferenceRestrictionsOnDirectAndIndirect:
        return self[1]


class OrReferenceRestrictions(ReferenceRestrictions):
    def __init__(self,
                 or_restriction_parts: list,
                 resolver_container_2_error_message_if_no_matching_part: types.FunctionType = None):
        self._parts = tuple(or_restriction_parts)
        self._container_2_error_message_if_no_matching_part = resolver_container_2_error_message_if_no_matching_part

    @property
    def parts(self) -> tuple:
        return self._parts

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: ResolverContainer) -> FailureInfo:
        resolver = container.resolver
        assert isinstance(resolver, SymbolValueResolver)  # Type info for IDE
        for part in self._parts:
            assert isinstance(part, OrRestrictionPart)  # Type info for IDE
            if part.selector == resolver.value_type:
                return part.restriction.is_satisfied_by(symbol_table, symbol_name, container)
        return self._no_satisfied_restriction(symbol_name, resolver, container)

    def _no_satisfied_restriction(self,
                                  symbol_name: str,
                                  resolver: SymbolValueResolver,
                                  value: ResolverContainer) -> FailureOfDirectReference:
        if self._container_2_error_message_if_no_matching_part is not None:
            msg = self._container_2_error_message_if_no_matching_part(value)
        else:
            msg = self._default_error_message(symbol_name, value, resolver)
        return FailureOfDirectReference(ValueRestrictionFailure(msg))

    def _default_error_message(self,
                               symbol_name: str,
                               container: ResolverContainer,
                               resolver: SymbolValueResolver) -> str:
        from exactly_lib.help_texts.test_case.instructions import assign_symbol as help_texts
        accepted_value_types = ', '.join([help_texts.TYPE_INFO_DICT[part.selector].type_name
                                          for part in self._parts])
        lines = ([
                     'Invalid type, of symbol "{}"'.format(symbol_name)
                 ] +
                 defined_at_line__err_msg_lines(container.definition_source) +
                 [
                     '',
                     'Accepted : ' + accepted_value_types,
                     'Found    : ' + help_texts.TYPE_INFO_DICT[resolver.value_type].type_name,
                 ])
        return '\n'.join(lines)


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


class ReferenceRestrictionsVisitor:
    def visit(self, x: ReferenceRestrictions):
        if isinstance(x, ReferenceRestrictionsOnDirectAndIndirect):
            return self.visit_direct_and_indirect(x)
        if isinstance(x, OrReferenceRestrictions):
            return self.visit_or(x)
        raise TypeError('%s is not an instance of %s' % (str(x), str(ReferenceRestrictions)))

    def visit_direct_and_indirect(self, x: ReferenceRestrictionsOnDirectAndIndirect):
        raise NotImplementedError()

    def visit_or(self, x: OrReferenceRestrictions):
        raise NotImplementedError()


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

    def _accepted_relativities_lines() -> list:
        ret_val = []
        header = '   '
        if accepted.absolute:
            ret_val.append(header + file_ref_texts.RELATIVITY_DESCRIPTION_ABSOLUTE)
        for rel_opt in accepted.rel_option_types:
            ret_val.append(header + option_description(rel_opt))

        return ret_val

    lines = ([
                 'Unaccepted relativity, of {} symbol "{}"'.format(help_texts.TYPE_INFO_DICT[ValueType.PATH].type_name,
                                                                   symbol_name)
             ] +
             defined_at_line__err_msg_lines(container.definition_source) +
             [
                 '',
                 'Found    : ' + _render_actual_relativity(),
                 'Accepted : ',
             ])
    lines.extend(_accepted_relativities_lines())
    return '\n'.join(lines)


def _invalid_type_header_lines(expected: ValueType,
                               actual: ValueType,
                               symbol_name: str,
                               container: ResolverContainer) -> list:
    from exactly_lib.help_texts.test_case.instructions import assign_symbol as help_texts
    ret_val = ([
                   'Invalid type, of symbol "{}"'.format(symbol_name)
               ] +
               defined_at_line__err_msg_lines(container.definition_source) +
               [
                   '',
                   'Expected : ' + help_texts.TYPE_INFO_DICT[expected].type_name,
                   'Found    : ' + help_texts.TYPE_INFO_DICT[actual].type_name,
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
