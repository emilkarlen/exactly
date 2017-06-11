import types

from exactly_lib.common.help.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.argument_rendering import cl_syntax, path_syntax
from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names_plain import SETUP_PHASE_NAME
from exactly_lib.symbol.value_structure import ValueType
from exactly_lib.util.cli_syntax.elements import argument as a

PATH_TYPE = 'path'
STRING_TYPE = 'string'
EQUALS_ARGUMENT = '='

SYMBOL_NAME = 'NAME'
STRING_VALUE = 'STRING'

PATH_SUFFIX_IS_REQUIRED = False

ASSIGN_SYMBOL_INSTRUCTION_CROSS_REFERENCE = TestCasePhaseInstructionCrossReference(SETUP_PHASE_NAME,
                                                                                   SYMBOL_DEFINITION_INSTRUCTION_NAME)


class TypeInfo(tuple):
    def __new__(cls,
                type_name: str,
                def_instruction_syntax_lines_function):
        return tuple.__new__(cls, (type_name,
                                   def_instruction_syntax_lines_function))

    @property
    def type_name(self) -> str:
        return self[0]

    @property
    def def_instruction_syntax_lines_function(self) -> types.FunctionType:
        """
        :return: A function, that takes no argument, and gives a list of
        strings.  Each string is a command line syntax for defining a symbol of the
        type that this object represents.
        """
        return self[1]


def _def_instruction_syntax_lines_function__string() -> list:
    return [
        definition_of_type_string()
    ]


def _def_instruction_syntax_lines_function__path() -> list:
    return [
        definition_of_type_path()
    ]


TYPE_INFO_DICT = {
    ValueType.STRING:
        TypeInfo(STRING_TYPE,
                 _def_instruction_syntax_lines_function__string),
    ValueType.PATH:
        TypeInfo(PATH_TYPE,
                 _def_instruction_syntax_lines_function__path),
}


def definition_of_type_string() -> str:
    string_type = a.Single(a.Multiplicity.MANDATORY, a.Constant(STRING_TYPE))
    string_value = a.Single(a.Multiplicity.MANDATORY, a.Named(STRING_VALUE))
    arguments_for_string_type = [
        string_type,
        _symbol_name(),
        _equals(),
        string_value,
    ]
    return cl_syntax.cl_syntax_for_args(arguments_for_string_type)


def definition_of_type_path() -> str:
    path_type = a.Single(a.Multiplicity.MANDATORY, a.Constant(PATH_TYPE))
    arguments_for_path_type = [
        path_type,
        _symbol_name(),
        _equals(),
    ]
    arguments_for_path_type.extend(
        path_syntax.mandatory_path_with_optional_relativity(
            path_syntax.PATH_ARGUMENT,
            True,
            PATH_SUFFIX_IS_REQUIRED))
    return cl_syntax.cl_syntax_for_args(arguments_for_path_type)


def _symbol_name() -> a.ArgumentUsage:
    return a.Single(a.Multiplicity.MANDATORY, a.Named(SYMBOL_NAME))


def _equals() -> a.ArgumentUsage:
    return a.Single(a.Multiplicity.MANDATORY, a.Constant(EQUALS_ARGUMENT))
