from types import MappingProxyType
from typing import List, Sequence

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.argument_rendering import cl_syntax, path_syntax
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.definitions.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
from exactly_lib.definitions.type_system import TypeNameAndCrossReferenceId
from exactly_lib.symbol.value_type import WithStrRenderingType, ValueType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.table import TableCell

ASSIGNMENT_ARGUMENT = instruction_arguments.ASSIGNMENT_OPERATOR

TYPE_SYNTAX_ELEMENT = 'TYPE'

VALUE_SYNTAX_ELEMENT = 'VALUE'

PATH_SUFFIX_IS_REQUIRED = True

DEFINE_SYMBOL_INSTRUCTION_CROSS_REFERENCE = phase_infos.SETUP.instruction_cross_reference_target(
    SYMBOL_DEFINITION_INSTRUCTION_NAME)


def def_instruction_argument_syntax() -> List[a.ArgumentUsage]:
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
                value_arguments: List[a.ArgumentUsage]):
        return tuple.__new__(cls, (type_info,
                                   value_arguments))

    @property
    def type_info(self) -> TypeNameAndCrossReferenceId:
        return self[0]

    @property
    def identifier(self) -> str:
        return self.type_info.identifier

    @property
    def value_arguments(self) -> List[a.ArgumentUsage]:
        return self[1]

    @property
    def def_instruction_arguments(self) -> List[a.ArgumentUsage]:
        before_value = [
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(self.identifier)),
            _SYMBOL_NAME,
            _EQUALS,
        ]
        return before_value + self.value_arguments


def _standard_type_value_args(type_info: TypeNameAndCrossReferenceId,
                              value_multiplicity: a.Multiplicity = a.Multiplicity.MANDATORY) -> List[a.ArgumentUsage]:
    return [a.Single(value_multiplicity,
                     a.Named(type_info.syntax_element_name))]


_SYMBOL_NAME = a.Single(a.Multiplicity.MANDATORY,
                        syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument)

_EQUALS = a.Single(a.Multiplicity.MANDATORY,
                   a.Constant(ASSIGNMENT_ARGUMENT))

TYPE_W_STR_RENDERING_INFO_DICT = MappingProxyType({
    WithStrRenderingType.STRING:
        TypeInfo(types.STRING_TYPE_INFO,
                 _standard_type_value_args(types.STRING_TYPE_INFO,
                                           a.Multiplicity.MANDATORY)),

    WithStrRenderingType.PATH:
        TypeInfo(types.PATH_TYPE_INFO,
                 path_syntax.mandatory_path_with_optional_relativity(
                     a.Named(types.PATH_TYPE_INFO.syntax_element_name),
                     PATH_SUFFIX_IS_REQUIRED)),

    WithStrRenderingType.LIST:
        TypeInfo(types.LIST_TYPE_INFO,
                 [syntax_elements.LIST_SYNTAX_ELEMENT.single_mandatory]),
})


def _logic_type_info(type_info: TypeNameAndCrossReferenceId) -> TypeInfo:
    return TypeInfo(type_info, _standard_type_value_args(type_info))


ANY_TYPE_INFO_DICT = {
    ValueType.STRING:
        TYPE_W_STR_RENDERING_INFO_DICT[WithStrRenderingType.STRING],
    ValueType.PATH:
        TYPE_W_STR_RENDERING_INFO_DICT[WithStrRenderingType.PATH],
    ValueType.LIST:
        TYPE_W_STR_RENDERING_INFO_DICT[WithStrRenderingType.LIST],

    ValueType.INTEGER_MATCHER:
        _logic_type_info(types.INTEGER_MATCHER_TYPE_INFO),

    ValueType.LINE_MATCHER:
        _logic_type_info(types.LINE_MATCHER_TYPE_INFO),

    ValueType.FILE_MATCHER:
        _logic_type_info(types.FILE_MATCHER_TYPE_INFO),

    ValueType.FILES_MATCHER:
        _logic_type_info(types.FILES_MATCHER_TYPE_INFO),

    ValueType.STRING_SOURCE:
        _logic_type_info(types.STRING_SOURCE_TYPE_INFO),

    ValueType.STRING_MATCHER:
        _logic_type_info(types.STRING_MATCHER_TYPE_INFO),

    ValueType.STRING_TRANSFORMER:
        _logic_type_info(types.STRING_TRANSFORMER_TYPE_INFO),

    ValueType.PROGRAM:
        _logic_type_info(types.PROGRAM_TYPE_INFO),

    ValueType.FILES_CONDITION:
        _logic_type_info(types.FILES_CONDITION_TYPE_INFO),
}


def def_syntax_table_row(value_type: ValueType) -> List[TableCell]:
    type_info = ANY_TYPE_INFO_DICT[value_type]
    arg_parts = _arg_parts_for(value_type,
                               syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument.name,
                               cl_syntax.cl_syntax_for_args(type_info.value_arguments))
    return list(map(docs.text_cell, arg_parts))


def def_syntax_string(value_type: ValueType,
                      symbol_name: str,
                      symbol_value: str) -> str:
    arg_parts = _arg_parts_for(value_type, symbol_name, symbol_value)
    return ' '.join(arg_parts)


def _arg_parts_for(value_type: ValueType,
                   symbol_name: str,
                   symbol_value: str) -> List[str]:
    type_info = ANY_TYPE_INFO_DICT[value_type]
    return [
        instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME,
        type_info.identifier,
        symbol_name,
        ASSIGNMENT_ARGUMENT,
        symbol_value,
    ]


def def_syntax_table(value_types: Sequence[ValueType]) -> docs.ParagraphItem:
    return docs.plain_table(map(def_syntax_table_row, value_types),
                            column_separator=' ')
