from exactly_lib.help_texts import type_system, instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax, path_syntax
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.help_texts.entity.types import STRING_TYPE_INFO, PATH_TYPE_INFO, LIST_TYPE_INFO, \
    LINE_MATCHER_TYPE_INFO, FILE_MATCHER_TYPE_INFO, LINES_TRANSFORMER_TYPE_INFO, TypeNameAndCrossReferenceId
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names_plain import SETUP_PHASE_NAME
from exactly_lib.type_system.value_type import DataValueType, ValueType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs

ASSIGNMENT_ARGUMENT = instruction_arguments.ASSIGNMENT_OPERATOR

TYPE_SYNTAX_ELEMENT = 'TYPE'

VALUE_SYNTAX_ELEMENT = 'VALUE'

PATH_SUFFIX_IS_REQUIRED = False

DEFINE_SYMBOL_INSTRUCTION_CROSS_REFERENCE = TestCasePhaseInstructionCrossReference(SETUP_PHASE_NAME,
                                                                                   SYMBOL_DEFINITION_INSTRUCTION_NAME)


def def_instruction_argument_syntax() -> list:
    return [
        a.Single(a.Multiplicity.MANDATORY,
                 a.Named(TYPE_SYNTAX_ELEMENT)),

        a.Single(a.Multiplicity.MANDATORY,
                 syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument),

        a.Single(a.Multiplicity.MANDATORY,
                 a.Constant(ASSIGNMENT_ARGUMENT)),

        a.Single(a.Multiplicity.MANDATORY,
                 a.Named(VALUE_SYNTAX_ELEMENT)),
    ]


class TypeInfo(tuple):
    def __new__(cls,
                type_info: TypeNameAndCrossReferenceId,
                value_arguments: list):
        return tuple.__new__(cls, (type_info,
                                   value_arguments))

    @property
    def type_info(self) -> TypeNameAndCrossReferenceId:
        return self[0]

    @property
    def identifier(self) -> str:
        return self.type_info.identifier

    @property
    def value_arguments(self) -> list:
        return self[1]

    @property
    def def_instruction_arguments(self) -> list:
        before_value = [
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(self.identifier)),
            _SYMBOL_NAME,
            _EQUALS,
        ]
        return before_value + self.value_arguments


def _standard_type_value_args(type_info: TypeNameAndCrossReferenceId,
                              value_multiplicity: a.Multiplicity = a.Multiplicity.OPTIONAL) -> list:
    return [a.Single(value_multiplicity,
                     a.Named(type_info.syntax_element_name))]


_SYMBOL_NAME = a.Single(a.Multiplicity.MANDATORY,
                        syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument)

_EQUALS = a.Single(a.Multiplicity.MANDATORY,
                   a.Constant(ASSIGNMENT_ARGUMENT))

DATA_TYPE_INFO_DICT = {
    DataValueType.STRING:
        TypeInfo(STRING_TYPE_INFO,
                 _standard_type_value_args(STRING_TYPE_INFO,
                                           a.Multiplicity.MANDATORY)),

    DataValueType.PATH:
        TypeInfo(PATH_TYPE_INFO,
                 path_syntax.mandatory_path_with_optional_relativity(
                     a.Named(PATH_TYPE_INFO.syntax_element_name),
                     PATH_SUFFIX_IS_REQUIRED)),

    DataValueType.LIST:
        TypeInfo(LIST_TYPE_INFO,
                 [a.Single(a.Multiplicity.ZERO_OR_MORE,
                           a.Named(type_system.LIST_ELEMENT))]),
}

ANY_TYPE_INFO_DICT = {
    ValueType.STRING:
        DATA_TYPE_INFO_DICT[DataValueType.STRING],
    ValueType.PATH:
        DATA_TYPE_INFO_DICT[DataValueType.PATH],
    ValueType.LIST:
        DATA_TYPE_INFO_DICT[DataValueType.LIST],

    ValueType.LINE_MATCHER:
        TypeInfo(LINE_MATCHER_TYPE_INFO,
                 _standard_type_value_args(LINE_MATCHER_TYPE_INFO)),

    ValueType.FILE_MATCHER:
        TypeInfo(FILE_MATCHER_TYPE_INFO,
                 _standard_type_value_args(FILE_MATCHER_TYPE_INFO)),

    ValueType.LINES_TRANSFORMER:
        TypeInfo(LINES_TRANSFORMER_TYPE_INFO,
                 _standard_type_value_args(LINES_TRANSFORMER_TYPE_INFO)),
}


def def_syntax_table_row(value_type: ValueType) -> list:
    type_info = ANY_TYPE_INFO_DICT[value_type]
    arg_parts = [
        instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME,
        type_info.identifier,
        syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument.name,
        ASSIGNMENT_ARGUMENT,
        cl_syntax.cl_syntax_for_args(type_info.value_arguments),
    ]
    return list(map(docs.text_cell, arg_parts))


def def_syntax_table(value_types) -> docs.ParagraphItem:
    return docs.plain_table(map(def_syntax_table_row, value_types),
                            column_separator=' ')
