from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.concepts.names_and_cross_references import CURRENT_WORKING_DIRECTORY_CONCEPT_INFO
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.test_case.instructions.assign_symbol import ASSIGN_SYMBOL_INSTRUCTION_CROSS_REFERENCE
from exactly_lib.instructions.utils.arg_parse.token_stream_parse import TokenParser
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.parser_implementations.token_stream import TokenStream
from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_ref_check import pre_or_post_sds_failure_message_or_none, FileRefCheck
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render.cli_program_syntax import render_argument
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure import lists


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


TYPE_NAME_SYMLINK = 'symlink'
TYPE_NAME_REGULAR = 'file'
TYPE_NAME_DIRECTORY = 'dir'

FILE_TYPE_OPTIONS = [
    (file_properties.FileType.SYMLINK, a.OptionName(long_name=TYPE_NAME_SYMLINK)),
    (file_properties.FileType.REGULAR, a.OptionName(long_name=TYPE_NAME_REGULAR)),
    (file_properties.FileType.DIRECTORY, a.OptionName(long_name=TYPE_NAME_DIRECTORY)),
]

_TYPE_ARGUMENT_STR = 'TYPE'

_PATH_ARGUMENT = path_syntax.PATH_ARGUMENT

_DEFAULT_FILE_PROPERTIES_CHECK = file_properties.must_exist(follow_symlinks=False)

_REL_OPTION_CONFIG = RelOptionArgumentConfiguration(
    RelOptionsConfiguration(
        PathRelativityVariants(
            {RelOptionType.REL_ACT,
             RelOptionType.REL_TMP,
             RelOptionType.REL_CWD},
            True),
        True,
        RelOptionType.REL_CWD),
    _PATH_ARGUMENT.name,
    True)


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        self.type_argument = a.Named(_TYPE_ARGUMENT_STR)
        super().__init__(name, {
            'PATH': _PATH_ARGUMENT.name,
            'TYPE': _TYPE_ARGUMENT_STR,
            'SYM_LNK': file_properties.type_name[file_properties.FileType.SYMLINK],
        })

    def single_line_description(self) -> str:
        return 'Tests the existence, and optionally type, of a file'

    def main_description_rest(self) -> list:
        text = """\
        PASS if, and only if, {PATH} exists, and is a file of the given type.


        If {TYPE} is not given, {PATH} may be any type of file.
        """
        specific_for_instruction = self._paragraphs(text)
        default_relativity = rel_path_doc.default_relativity_for_rel_opt_type(_PATH_ARGUMENT.name,
                                                                              _REL_OPTION_CONFIG.options.default_option)
        path_syntax_paragraphs = dt.paths_uses_posix_syntax()
        return specific_for_instruction + default_relativity + path_syntax_paragraphs

    def invokation_variants(self) -> list:
        type_arguments = [a.Single(a.Multiplicity.OPTIONAL, self.type_argument)]
        path_arguments = path_syntax.mandatory_path_with_optional_relativity(
            _PATH_ARGUMENT,
            _REL_OPTION_CONFIG.options.is_rel_symbol_option_accepted,
            _REL_OPTION_CONFIG.path_suffix_is_required)
        arguments = type_arguments + path_arguments

        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              []),
        ]

    def syntax_element_descriptions(self) -> list:
        type_elements = [
            SyntaxElementDescription(self.type_argument.name,
                                     [self._file_type_list()], []),
        ]
        path_elements = rel_path_doc.relativity_syntax_element_descriptions(_PATH_ARGUMENT,
                                                                            _REL_OPTION_CONFIG.options)
        all_elements = type_elements + path_elements

        return all_elements

    def _see_also_cross_refs(self) -> list:
        concepts = rel_path_doc.see_also_concepts(_REL_OPTION_CONFIG.options)
        rel_path_doc.add_concepts_if_not_listed(concepts, [CURRENT_WORKING_DIRECTORY_CONCEPT_INFO])
        refs = [concept.cross_reference_target for concept in concepts]
        refs.append(ASSIGN_SYMBOL_INSTRUCTION_CROSS_REFERENCE)
        return refs

    def _file_type_list(self) -> core.ParagraphItem:
        def type_description(file_type: file_properties.FileType) -> list:
            text = 'Tests if {PATH} is a {file_type}, or a {SYM_LNK} to a {file_type}.'
            if file_type is file_properties.FileType.SYMLINK:
                text = 'Tests if {PATH} is a {SYM_LNK} (link target may or may not exist).'
            extra = {
                'file_type': file_properties.type_name[file_type],
            }
            return self._paragraphs(text, extra)

        sort_value__list_items = [
            (file_properties.type_name[file_type],
             lists.HeaderContentListItem(self._text(render_argument(a.Option(option_name))),
                                         type_description(file_type)))
            for file_type, option_name in FILE_TYPE_OPTIONS]
        sort_value__list_items.sort(key=lambda type_name__list_item: type_name__list_item[0])
        list_items = [type_name__list_item[1]
                      for type_name__list_item in sort_value__list_items]
        return lists.HeaderContentList(list_items,
                                       lists.Format(lists.ListType.VARIABLE_LIST))


class Parser(InstructionParserThatConsumesCurrentLine):
    def __init__(self):
        self.format_map = {
            'PATH': _PATH_ARGUMENT.name,
        }

    def _parse(self, rest_of_line: str) -> AssertPhaseInstruction:
        tokens = TokenParser(TokenStream(rest_of_line),
                             self.format_map)
        file_properties_check = tokens.consume_and_handle_first_matching_option(
            _DEFAULT_FILE_PROPERTIES_CHECK,
            _file_type_2_file_properties_check,
            FILE_TYPE_OPTIONS)
        file_ref_resolver = tokens.consume_file_ref(_REL_OPTION_CONFIG)
        tokens.report_superfluous_arguments_if_not_at_eol()
        return _Instruction(file_ref_resolver, file_properties_check)


def _file_type_2_file_properties_check(file_type: file_properties.FileType
                                       ) -> file_properties.FilePropertiesCheck:
    follow_sym_links = file_type is not file_properties.FileType.SYMLINK
    return file_properties.must_exist_as(file_type,
                                         follow_sym_links)


class _Instruction(AssertPhaseInstruction):
    def __init__(self,
                 file_ref_resolver: FileRefResolver,
                 expected_file_properties: file_properties.FilePropertiesCheck):
        self._file_ref_resolver = file_ref_resolver
        self._expected_file_properties = expected_file_properties

    def symbol_usages(self) -> list:
        return self._file_ref_resolver.references

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        failure_message = pre_or_post_sds_failure_message_or_none(
            FileRefCheck(self._file_ref_resolver,
                         self._expected_file_properties),
            environment.path_resolving_environment_pre_or_post_sds)
        return pfh.new_pfh_fail_if_has_failure_message(failure_message)
