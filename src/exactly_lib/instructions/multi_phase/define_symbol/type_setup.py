from typing import List

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.entity.types import TypeNameAndCrossReferenceId
from exactly_lib.definitions.test_case.instructions import define_symbol as syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from . import type_parser


class TypeSetup:
    def __init__(self,
                 type_info: TypeNameAndCrossReferenceId,
                 parser: type_parser.TypeValueParser,
                 value_arguments: List[a.ArgumentUsage],
                 ):
        self.type_info = type_info
        self.parser = parser
        self.value_type = type_info.value_type
        self.value_arguments = value_arguments

    @staticmethod
    def new_with_std_syntax(
            type_info: TypeNameAndCrossReferenceId,
            parser: type_parser.TypeValueParser,
    ) -> 'TypeSetup':
        return TypeSetup(
            type_info,
            parser,
            syntax.ANY_TYPE_INFO_DICT[type_info.value_type].value_arguments,
        )


TYPE_SETUPS_LIST = [
    TypeSetup(types.STRING_TYPE_INFO,
              type_parser.StringParser(),
              [
                  a.Choice(a.Multiplicity.MANDATORY,
                           [instruction_arguments.STRING,
                            instruction_arguments.HERE_DOCUMENT])
              ]),
    TypeSetup.new_with_std_syntax(types.LIST_TYPE_INFO,
                                  type_parser.ListParser()),
    TypeSetup.new_with_std_syntax(types.PATH_TYPE_INFO,
                                  type_parser.PathParser()),
    TypeSetup.new_with_std_syntax(types.LINE_MATCHER_TYPE_INFO,
                                  type_parser.LineMatcherParser()),
    TypeSetup.new_with_std_syntax(types.FILE_MATCHER_TYPE_INFO,
                                  type_parser.FileMatcherParser()),
    TypeSetup.new_with_std_syntax(types.FILES_MATCHER_TYPE_INFO,
                                  type_parser.FilesMatcherParser()),
    TypeSetup.new_with_std_syntax(types.STRING_MATCHER_TYPE_INFO,
                                  type_parser.StringMatcherParser()),
    TypeSetup.new_with_std_syntax(types.FILES_CONDITION_TYPE_INFO,
                                  type_parser.FilesConditionParser()),
    TypeSetup.new_with_std_syntax(types.STRING_TRANSFORMER_TYPE_INFO,
                                  type_parser.StringTransformerParser()),
    TypeSetup.new_with_std_syntax(types.PROGRAM_TYPE_INFO,
                                  type_parser.ProgramParser()),
]

TYPE_SETUPS = {
    ts.type_info.identifier: ts
    for ts in TYPE_SETUPS_LIST
}
