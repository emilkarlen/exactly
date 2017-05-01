from exactly_lib.symbol.concrete_values import FileRefResolver, StringResolver, SymbolValueResolver, ValueType
from exactly_lib.symbol.value_structure import ValueRestriction, Value
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants
from exactly_lib.test_case_file_structure.relativity_validation import is_satisfied_by
from exactly_lib.util.symbol_table import SymbolTable


class NoRestriction(ValueRestriction):
    """
    No restriction - a restriction that any value satisfies.
    """

    def is_satisfied_by(self, symbol_table: SymbolTable, value: Value) -> str:
        return None


class StringRestriction(ValueRestriction):
    """
    Restriction to string values.
    """

    def is_satisfied_by(self, symbol_table: SymbolTable, value: Value) -> str:
        if not isinstance(value, StringResolver):
            return _invalid_type_msg__string_expected(value)
        return None


class FileRefRelativityRestriction(ValueRestriction):
    """
    Restricts to `FileRefValue` and `PathRelativityVariants`
    """

    def __init__(self, accepted: PathRelativityVariants):
        self._accepted = accepted

    def is_satisfied_by(self, symbol_table: SymbolTable, value: Value) -> str:
        if not isinstance(value, FileRefResolver):
            #  TODO [val-def] Error message should be human readable
            return 'Not a FileRefValue: ' + str(value)
        file_ref = value.resolve(symbol_table)
        actual_relativity = file_ref.relativity()
        return is_satisfied_by(actual_relativity, self._accepted)

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

    def is_satisfied_by(self, symbol_table: SymbolTable, value: Value) -> str:
        string_result = self.string_restriction.is_satisfied_by(symbol_table, value)
        if not string_result:
            return None
        file_ref_result = self.file_ref_restriction.is_satisfied_by(symbol_table, value)
        if file_ref_result:
            msg = 'Satisfies neither string or file-ref restriction:string: \n{}\file-ref: {}'.format(
                string_result,
                file_ref_result)
            return msg
        return None

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


def _invalid_type_msg__string_expected(actual: Value) -> str:
    if not isinstance(actual, SymbolValueResolver):
        raise TypeError('Symbol table contains a value that is not a {}: {}'.format(
            type(SymbolValueResolver),
            str(actual)
        ))
    assert isinstance(actual, SymbolValueResolver)  # Type info for IDE
    lines = _invalid_type_header_lines(ValueType.STRING, actual.value_type)
    return '\n'.join(lines)


def _invalid_type_header_lines(expected: ValueType,
                               actual: ValueType) -> list:
    from exactly_lib.help_texts.test_case.instructions import assign_symbol as help_texts
    from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
    from exactly_lib.help_texts.names.formatting import InstructionName
    def_name_emphasised = InstructionName(SYMBOL_DEFINITION_INSTRUCTION_NAME).emphasis
    ret_val = [
        'Invalid type of symbol',
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
