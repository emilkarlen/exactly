import types

from exactly_lib.help_texts import type_system
from exactly_lib.help_texts.argument_rendering import cl_syntax, path_syntax
from exactly_lib.help_texts.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.entity.types import STRING_CONCEPT_INFO, PATH_CONCEPT_INFO, LIST_CONCEPT_INFO, \
    LINE_MATCHER_CONCEPT_INFO, FILE_MATCHER_CONCEPT_INFO, LINES_TRANSFORMER_CONCEPT_INFO, TypeNameAndCrossReferenceId
from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names_plain import SETUP_PHASE_NAME
from exactly_lib.type_system.value_type import DataValueType, ValueType
from exactly_lib.util.cli_syntax.elements import argument as a

EQUALS_ARGUMENT = '='

SYMBOL_NAME = 'NAME'

PATH_SUFFIX_IS_REQUIRED = False

SYMBOL_NAME_SYNTAX_DESCRIPTION = 'A combination of alphanumeric characters and underscores.'

DEFINE_SYMBOL_INSTRUCTION_CROSS_REFERENCE = TestCasePhaseInstructionCrossReference(SETUP_PHASE_NAME,
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
        TypeInfo(STRING_CONCEPT_INFO.identifier,
                 _def_instruction_syntax_lines_function__string),
    DataValueType.PATH:
        TypeInfo(PATH_CONCEPT_INFO.identifier,
                 _def_instruction_syntax_lines_function__path),
    DataValueType.LIST:
        TypeInfo(LIST_CONCEPT_INFO.identifier,
                 _def_instruction_syntax_lines_function__list),
}

ANY_TYPE_INFO_DICT = {
    ValueType.STRING:
        TypeInfo(STRING_CONCEPT_INFO.identifier,
                 _def_instruction_syntax_lines_function__string),
    ValueType.PATH:
        TypeInfo(PATH_CONCEPT_INFO.identifier,
                 _def_instruction_syntax_lines_function__path),
    ValueType.LIST:
        TypeInfo(LIST_CONCEPT_INFO.identifier,
                 _def_instruction_syntax_lines_function__list),
    ValueType.LINE_MATCHER:
        TypeInfo(LINE_MATCHER_CONCEPT_INFO.identifier,
                 _def_instruction_syntax_lines_function__lines_transformer),
    ValueType.FILE_MATCHER:
        TypeInfo(FILE_MATCHER_CONCEPT_INFO.identifier,
                 _def_instruction_syntax_lines_function__file_matcher),
    ValueType.LINES_TRANSFORMER:
        TypeInfo(LINES_TRANSFORMER_CONCEPT_INFO.identifier,
                 _def_instruction_syntax_lines_function__lines_transformer),
}


def definition_of_type_string() -> str:
    return _standard_definition(STRING_CONCEPT_INFO,
                                a.Multiplicity.MANDATORY)


def definition_of_type_path() -> str:
    return _def_of(PATH_CONCEPT_INFO.identifier,
                   path_syntax.mandatory_path_with_optional_relativity(
                       a.Named(PATH_CONCEPT_INFO.syntax_element_name),
                       PATH_SUFFIX_IS_REQUIRED)
                   )


def definition_of_type_list() -> str:
    return _def_of(LIST_CONCEPT_INFO.identifier,
                   [a.Single(a.Multiplicity.ZERO_OR_MORE,
                             a.Named(type_system.LIST_ELEMENT))])


def definition_of_type_line_matcher() -> str:
    return _standard_definition(LINE_MATCHER_CONCEPT_INFO)


def definition_of_type_file_matcher() -> str:
    return _standard_definition(FILE_MATCHER_CONCEPT_INFO)


def definition_of_type_lines_transformer() -> str:
    return _standard_definition(LINES_TRANSFORMER_CONCEPT_INFO)


def _standard_definition(type_info: TypeNameAndCrossReferenceId,
                         value_multiplicity: a.Multiplicity = a.Multiplicity.OPTIONAL) -> str:
    return _def_of(type_info.identifier,
                   [a.Single(value_multiplicity,
                             a.Named(type_info.syntax_element_name))])


def _def_of(type_token: str, value_arguments: list) -> str:
    arguments = [
        a.Single(a.Multiplicity.MANDATORY, a.Constant(type_token)),
        _symbol_name(),
        _equals(),
    ]
    arguments += value_arguments
    return cl_syntax.cl_syntax_for_args(arguments)


def _symbol_name() -> a.ArgumentUsage:
    return a.Single(a.Multiplicity.MANDATORY, a.Named(SYMBOL_NAME))


def _equals() -> a.ArgumentUsage:
    return a.Single(a.Multiplicity.MANDATORY, a.Constant(EQUALS_ARGUMENT))
