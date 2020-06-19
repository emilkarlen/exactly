from typing import Tuple, Callable, List, Sequence

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions import syntax_descriptions
from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.current_directory_and_path_type import def_instruction_rel_cd_description
from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.definitions.entity import types, syntax_elements, concepts
from exactly_lib.definitions.entity.types import TypeNameAndCrossReferenceId
from exactly_lib.definitions.test_case.instructions import define_symbol as syntax
from exactly_lib.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForErrorMessageStringResultAsHardError
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, from_parse_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolUsage, SymbolDefinition, \
    SymbolDependentValue
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_condition import parse as parse_files_condition
from exactly_lib.test_case_utils.files_condition.structure import FilesConditionSdv
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.parse import parse_path, parse_list
from exactly_lib.test_case_utils.parse.parse_here_doc_or_path import parse_string_or_here_doc_from_token_parser
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.type_system.data.string_or_path_ddvs import SourceType
from exactly_lib.type_system.logic.file_matcher import FileMatcherSdv
from exactly_lib.type_system.logic.files_matcher import FilesMatcherSdv
from exactly_lib.type_system.logic.line_matcher import LineMatcherSdv
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.line_source import LineSequence
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.table import TableCell


class _TypeSetup:
    def __init__(self,
                 type_info: TypeNameAndCrossReferenceId,
                 parser: Callable[[FileSystemLocationInfo, TokenParser], Tuple[bool, SymbolDependentValue]],
                 value_arguments: List[a.ArgumentUsage],
                 ):
        self.type_info = type_info
        self.parser = parser
        self.value_type = type_info.value_type
        self.value_arguments = value_arguments

    @staticmethod
    def new_with_std_syntax(
            type_info: TypeNameAndCrossReferenceId,
            parser: Callable[[FileSystemLocationInfo, TokenParser], Tuple[bool, SymbolDependentValue]],
    ) -> '_TypeSetup':
        return _TypeSetup(
            type_info,
            parser,
            syntax.ANY_TYPE_INFO_DICT[type_info.value_type].value_arguments,
        )


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        self.name = syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument
        self.string_value = syntax_elements.STRING_SYNTAX_ELEMENT.argument
        super().__init__(name,
                         {
                             'NAME': self.name.name,
                             'SYMBOL': concepts.SYMBOL_CONCEPT_INFO.name,
                         },
                         is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._tp.format('Defines {SYMBOL:a}')

    def _main_description_rest_body(self) -> List[ParagraphItem]:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            InvokationVariant(
                cl_syntax.cl_syntax_for_args(syntax.def_instruction_argument_syntax())
            )
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return ([
            SyntaxElementDescription(', '.join([syntax.TYPE_SYNTAX_ELEMENT,
                                                syntax.VALUE_SYNTAX_ELEMENT]),
                                     [self._types_table()]),

            rel_path_doc.path_element_with_all_relativities(
                _PATH_ARGUMENT.name,
                REL_OPTION_ARGUMENT_CONFIGURATION.options.default_option,
                def_instruction_rel_cd_description(_PATH_ARGUMENT.name)),

            SyntaxElementDescription(self.string_value.name,
                                     self._tp.fnap(syntax_descriptions.STRING_SYNTAX_ELEMENT_DESCRIPTION)),

            SyntaxElementDescription(self.name.name,
                                     self._tp.fnap(syntax_descriptions.SYMBOL_NAME_SYNTAX_DESCRIPTION)),
        ])

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        name_and_cross_refs = [concepts.SYMBOL_CONCEPT_INFO,
                               concepts.TYPE_CONCEPT_INFO,
                               concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO,
                               syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
                               syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT,
                               ]
        return name_and_cross_ref.cross_reference_id_list(name_and_cross_refs)

    @staticmethod
    def _types_table() -> docs.ParagraphItem:
        def type_row(type_setup: _TypeSetup) -> List[TableCell]:
            return [
                docs.text_cell(syntax_text(type_setup.type_info.identifier)),
                docs.text_cell(syntax_text(cl_syntax.cl_syntax_for_args(type_setup.value_arguments))),
            ]

        rows = [
            [
                docs.text_cell(syntax.TYPE_SYNTAX_ELEMENT),
                docs.text_cell(syntax.VALUE_SYNTAX_ELEMENT),
            ]
        ]

        rows += map(type_row, _TYPE_SETUPS_LIST)

        return docs.first_row_is_header_table(rows)


class TheInstructionEmbryo(embryo.InstructionEmbryo[None]):
    def __init__(self, symbol: SymbolDefinition):
        self.symbol = symbol

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return [self.symbol]

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices,
             ):
        self.custom_main(environment.symbols)

    def custom_main(self, symbols: SymbolTable):
        symbols.put(self.symbol.name,
                    self.symbol.symbol_container)


class EmbryoParser(embryo.InstructionEmbryoParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> TheInstructionEmbryo:
        first_line_number = source.current_line_number
        instruction_name_prefix = source.current_line_text[:source.column_index]
        remaining_source_before = source.remaining_source

        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True,
                               consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            symbol_name, value_type, value_sdv = _parse(fs_location_info, token_parser)

        remaining_source_after = source.remaining_source
        num_chars_consumed = len(remaining_source_before) - len(remaining_source_after)
        parsed_str = remaining_source_before[:num_chars_consumed]
        source_lines = LineSequence(first_line_number,
                                    (instruction_name_prefix + parsed_str).splitlines())

        source_info = fs_location_info.current_source_file.source_location_info_for(source_lines)
        sym_def = SymbolDefinition(symbol_name,
                                   SymbolContainer(value_sdv,
                                                   value_type,
                                                   source_info))

        return TheInstructionEmbryo(sym_def)


PARTS_PARSER = PartsParserFromEmbryoParser(EmbryoParser(),
                                           MainStepResultTranslatorForErrorMessageStringResultAsHardError())


def _parse(fs_location_info: FileSystemLocationInfo,
           parser: TokenParser) -> Tuple[str, ValueType, SymbolDependentValue]:
    type_str = parser.consume_mandatory_unquoted_string('SYMBOL-TYPE', True)

    if type_str not in _TYPE_SETUPS:
        err_msg = 'Invalid type: {}\nExpecting one of {}'.format(type_str, _TYPES_LIST_IN_ERR_MSG)
        raise SingleInstructionInvalidArgumentException(err_msg)

    type_setup = _TYPE_SETUPS[type_str]

    name_str = parser.consume_mandatory_unquoted_string('SYMBOL-NAME', True)

    if not symbol_syntax.is_symbol_name(name_str):
        err_msg = symbol_syntax.invalid_symbol_name_error(name_str)
        raise SingleInstructionInvalidArgumentException(err_msg)

    parser.consume_mandatory_constant_unquoted_string(syntax.ASSIGNMENT_ARGUMENT, True)

    consumes_whole_line, value_sdv = type_setup.parser(fs_location_info, parser)

    if not consumes_whole_line and not parser.is_at_eol:
        msg = 'Superfluous arguments: ' + parser.remaining_part_of_current_line
        raise SingleInstructionInvalidArgumentException(msg)

    return name_str, type_setup.value_type, value_sdv


_PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

REL_OPTIONS_CONFIGURATION = RelOptionsConfiguration(
    PathRelativityVariants(frozenset(RelOptionType), True),
    RelOptionType.REL_CWD)

REL_OPTION_ARGUMENT_CONFIGURATION = RelOptionArgumentConfiguration(REL_OPTIONS_CONFIGURATION,
                                                                   instruction_arguments.PATH_ARGUMENT,
                                                                   syntax.PATH_SUFFIX_IS_REQUIRED)

_MAIN_DESCRIPTION_REST = """\
Defines the symbol {NAME} to be a value of the given type.


{NAME} must not have been defined earlier.


The defined symbol is available in all following instructions and phases.
"""


def _parse_string(fs_location_info: FileSystemLocationInfo,
                  token_parser: TokenParser) -> Tuple[bool, DataTypeSdv]:
    source_type, sdv = parse_string_or_here_doc_from_token_parser(token_parser)
    return source_type == SourceType.HERE_DOC, sdv


def _parse_not_whole_line(parser: Callable[[FileSystemLocationInfo, TokenParser], SymbolDependentValue]
                          ) -> Callable[[FileSystemLocationInfo, TokenParser], Tuple[bool, SymbolDependentValue]]:
    def f(fs_location_info: FileSystemLocationInfo,
          tp: TokenParser) -> Tuple[bool, SymbolDependentValue]:
        return False, parser(fs_location_info, tp)

    return f


def _parse_path(fs_location_info: FileSystemLocationInfo,
                token_parser: TokenParser) -> DataTypeSdv:
    return parse_path.parse_path_from_token_parser(
        REL_OPTION_ARGUMENT_CONFIGURATION,
        token_parser,
        fs_location_info.current_source_file.abs_path_of_dir_containing_last_file_base_name)


def _parse_list(fs_location_info: FileSystemLocationInfo,
                token_parser: TokenParser) -> DataTypeSdv:
    return parse_list.parse_list_from_token_parser(token_parser)


def _parse_line_matcher(fs_location_info: FileSystemLocationInfo,
                        token_parser: TokenParser) -> LineMatcherSdv:
    return parse_line_matcher.parse_line_matcher_from_token_parser(token_parser,
                                                                   must_be_on_current_line=False)


def _parse_string_matcher(fs_location_info: FileSystemLocationInfo,
                          token_parser: TokenParser) -> StringMatcherSdv:
    return parse_string_matcher.parse_string_matcher(token_parser)


def _parse_file_matcher(fs_location_info: FileSystemLocationInfo,
                        token_parser: TokenParser) -> FileMatcherSdv:
    return parse_file_matcher.parse_sdv(token_parser, must_be_on_current_line=False)


def _parse_files_matcher(fs_location_info: FileSystemLocationInfo,
                         token_parser: TokenParser) -> FilesMatcherSdv:
    return parse_files_matcher.parse_files_matcher(token_parser,
                                                   must_be_on_current_line=False)


def _parse_files_condition(fs_location_info: FileSystemLocationInfo,
                           token_parser: TokenParser) -> FilesConditionSdv:
    return parse_files_condition.parse(token_parser,
                                       must_be_on_current_line=False)


def _parse_string_transformer(fs_location_info: FileSystemLocationInfo,
                              token_parser: TokenParser) -> StringTransformerSdv:
    return parse_string_transformer.parse_string_transformer_from_token_parser(
        token_parser,
        must_be_on_current_line=False
    )


def _parse_program(fs_location_info: FileSystemLocationInfo,
                   token_parser: TokenParser) -> Tuple[bool, ProgramSdv]:
    sdv = parse_program.parse_program(token_parser)
    return True, sdv


_TYPE_SETUPS_LIST = [
    _TypeSetup(types.STRING_TYPE_INFO,
               _parse_string,
               [
                   a.Choice(a.Multiplicity.MANDATORY,
                            [instruction_arguments.STRING,
                             instruction_arguments.HERE_DOCUMENT])
               ]),
    _TypeSetup.new_with_std_syntax(types.LIST_TYPE_INFO,
                                   _parse_not_whole_line(_parse_list)),
    _TypeSetup.new_with_std_syntax(types.PATH_TYPE_INFO,
                                   _parse_not_whole_line(_parse_path)),
    _TypeSetup.new_with_std_syntax(types.LINE_MATCHER_TYPE_INFO,
                                   _parse_not_whole_line(_parse_line_matcher)),
    _TypeSetup.new_with_std_syntax(types.FILE_MATCHER_TYPE_INFO,
                                   _parse_not_whole_line(_parse_file_matcher)),
    _TypeSetup.new_with_std_syntax(types.FILES_MATCHER_TYPE_INFO,
                                   _parse_not_whole_line(_parse_files_matcher)),
    _TypeSetup.new_with_std_syntax(types.STRING_MATCHER_TYPE_INFO,
                                   _parse_not_whole_line(_parse_string_matcher)),
    _TypeSetup.new_with_std_syntax(types.FILES_CONDITION_TYPE_INFO,
                                   _parse_not_whole_line(_parse_files_condition)),
    _TypeSetup.new_with_std_syntax(types.STRING_TRANSFORMER_TYPE_INFO,
                                   _parse_not_whole_line(_parse_string_transformer)),
    _TypeSetup.new_with_std_syntax(types.PROGRAM_TYPE_INFO, _parse_program),
]

_TYPE_SETUPS = {
    ts.type_info.identifier: ts
    for ts in _TYPE_SETUPS_LIST
}

_TYPES_LIST_IN_ERR_MSG = '|'.join(sorted(_TYPE_SETUPS.keys()))
