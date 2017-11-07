import types

from exactly_lib.help_texts import type_system, instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax, path_syntax
from exactly_lib.help_texts.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names_plain import SETUP_PHASE_NAME
from exactly_lib.type_system.value_type import DataValueType, ValueType
from exactly_lib.util.cli_syntax.elements import argument as a

EQUALS_ARGUMENT = '='

SYMBOL_NAME = 'NAME'

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


def _def_instruction_syntax_lines_function__list() -> list:
    return [
        definition_of_type_list()
    ]


def _def_instruction_syntax_lines_function__line_matcher() -> list:
    return [
        definition_of_type_line_matcher()
    ]


def _def_instruction_syntax_lines_function__file_matcher() -> list:
    return [
        definition_of_type_file_matcher()
    ]


def _def_instruction_syntax_lines_function__lines_transformer() -> list:
    return [
        definition_of_type_lines_transformer()
    ]


DATA_TYPE_INFO_DICT = {
    DataValueType.STRING:
        TypeInfo(type_system.STRING_TYPE,
                 _def_instruction_syntax_lines_function__string),
    DataValueType.PATH:
        TypeInfo(type_system.PATH_TYPE,
                 _def_instruction_syntax_lines_function__path),
    DataValueType.LIST:
        TypeInfo(type_system.LIST_TYPE,
                 _def_instruction_syntax_lines_function__list),
}

ANY_TYPE_INFO_DICT = {
    ValueType.STRING:
        TypeInfo(type_system.STRING_TYPE,
                 _def_instruction_syntax_lines_function__string),
    ValueType.PATH:
        TypeInfo(type_system.PATH_TYPE,
                 _def_instruction_syntax_lines_function__path),
    ValueType.LIST:
        TypeInfo(type_system.LIST_TYPE,
                 _def_instruction_syntax_lines_function__list),
    ValueType.LINE_MATCHER:
        TypeInfo(type_system.LINE_MATCHER_TYPE,
                 _def_instruction_syntax_lines_function__lines_transformer),
    ValueType.FILE_MATCHER:
        TypeInfo(type_system.FILE_MATCHER_TYPE,
                 _def_instruction_syntax_lines_function__file_matcher),
    ValueType.LINES_TRANSFORMER:
        TypeInfo(type_system.LINES_TRANSFORMER_TYPE,
                 _def_instruction_syntax_lines_function__lines_transformer),
}


def definition_of_type_string() -> str:
    type_token = a.Single(a.Multiplicity.MANDATORY, a.Constant(type_system.STRING_TYPE))
    string_value = a.Single(a.Multiplicity.MANDATORY, a.Named(type_system.STRING_VALUE))
    arguments = [
        type_token,
        _symbol_name(),
        _equals(),
        string_value,
    ]
    return cl_syntax.cl_syntax_for_args(arguments)


def definition_of_type_path() -> str:
    type_token = a.Single(a.Multiplicity.MANDATORY, a.Constant(type_system.PATH_TYPE))
    arguments = [
        type_token,
        _symbol_name(),
        _equals(),
    ]
    arguments.extend(
        path_syntax.mandatory_path_with_optional_relativity(
            instruction_arguments.PATH_ARGUMENT,
            PATH_SUFFIX_IS_REQUIRED))
    return cl_syntax.cl_syntax_for_args(arguments)


def definition_of_type_list() -> str:
    type_token = a.Single(a.Multiplicity.MANDATORY, a.Constant(type_system.LIST_TYPE))
    elements = a.Single(a.Multiplicity.ZERO_OR_MORE, a.Named(type_system.LIST_ELEMENT))
    arguments = [
        type_token,
        _symbol_name(),
        _equals(),
        elements,
    ]
    return cl_syntax.cl_syntax_for_args(arguments)


def definition_of_type_line_matcher() -> str:
    type_token = a.Single(a.Multiplicity.MANDATORY, a.Constant(type_system.LINE_MATCHER_TYPE))
    matcher = a.Single(a.Multiplicity.OPTIONAL, a.Named(type_system.LINE_MATCHER_VALUE))
    arguments = [
        type_token,
        _symbol_name(),
        _equals(),
        matcher,
    ]
    return cl_syntax.cl_syntax_for_args(arguments)


def definition_of_type_file_matcher() -> str:
    type_token = a.Single(a.Multiplicity.MANDATORY, a.Constant(type_system.FILE_MATCHER_TYPE))
    matcher = a.Single(a.Multiplicity.OPTIONAL, a.Named(type_system.FILE_MATCHER_VALUE))
    arguments = [
        type_token,
        _symbol_name(),
        _equals(),
        matcher,
    ]
    return cl_syntax.cl_syntax_for_args(arguments)


def definition_of_type_lines_transformer() -> str:
    type_token = a.Single(a.Multiplicity.MANDATORY, a.Constant(type_system.LINES_TRANSFORMER_TYPE))
    transformer = a.Single(a.Multiplicity.OPTIONAL, a.Named(type_system.LINES_TRANSFORMER_VALUE))
    arguments = [
        type_token,
        _symbol_name(),
        _equals(),
        transformer,
    ]
    return cl_syntax.cl_syntax_for_args(arguments)


def _symbol_name() -> a.ArgumentUsage:
    return a.Single(a.Multiplicity.MANDATORY, a.Named(SYMBOL_NAME))


def _equals() -> a.ArgumentUsage:
    return a.Single(a.Multiplicity.MANDATORY, a.Constant(EQUALS_ARGUMENT))
