from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.doc_format import syntax_text
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.parse.token_stream_parse import TokenParserExtra
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.element_parsers.misc_utils import new_token_stream
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction, WithAssertPhasePurpose
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_utils import file_properties, negation_of_predicate
from exactly_lib.test_case_utils.file_ref_check import pre_or_post_sds_failure_message_or_none, FileRefCheck
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render.cli_program_syntax import render_argument
from exactly_lib.util.textformat.structure import lists, structures as docs
from exactly_lib.util.textformat.utils import transform_list_to_table


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


NEGATION_OPERATOR = instruction_arguments.NEGATION_ARGUMENT_STR

FILE_TYPE_OPTIONS = [
    (file_type, a.OptionName(long_name=file_info.type_argument))
    for file_type, file_info in file_properties.TYPE_INFO.items()
]

_TYPE_ARGUMENT_STR = 'TYPE'

_PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

_DEFAULT_FILE_PROPERTIES_CHECK = file_properties.must_exist(follow_symlinks=False)

_REL_OPTION_CONFIG = RelOptionArgumentConfiguration(
    RelOptionsConfiguration(
        PathRelativityVariants(
            {RelOptionType.REL_CWD,
             RelOptionType.REL_HOME_ACT,
             RelOptionType.REL_ACT,
             RelOptionType.REL_TMP,
             },
            True),
        RelOptionType.REL_CWD),
    _PATH_ARGUMENT.name,
    True)


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase,
                                  WithAssertPhasePurpose):
    def __init__(self, name: str):
        self.type_argument = a.Named(_TYPE_ARGUMENT_STR)
        self.negation_argument = a.Constant(NEGATION_OPERATOR)
        super().__init__(name, {
            'PATH': _PATH_ARGUMENT.name,
            'TYPE': _TYPE_ARGUMENT_STR,
            'SYM_LNK': file_properties.TYPE_INFO[file_properties.FileType.SYMLINK].description,
            'NEGATION_OPERATOR': NEGATION_OPERATOR,
        })

    def single_line_description(self) -> str:
        return 'Tests the existence, and optionally type, of a file'

    def main_description_rest(self) -> list:
        return self._paragraphs(_PART_OF_MAIN_DESCRIPTION_REST_THAT_IS_SPECIFIC_FOR_THIS_INSTRUCTION)

    def invokation_variants(self) -> list:
        type_arguments = [a.Single(a.Multiplicity.OPTIONAL, self.type_argument)]
        negation_arguments = [negation_of_predicate.optional_negation_argument_usage()]
        path_arguments = path_syntax.mandatory_path_with_optional_relativity(
            _PATH_ARGUMENT,
            _REL_OPTION_CONFIG.path_suffix_is_required)
        arguments = negation_arguments + type_arguments + path_arguments

        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              []),
        ]

    def syntax_element_descriptions(self) -> list:
        negation_elements = [
            negation_of_predicate.syntax_element_description()
        ]
        type_elements = [
            SyntaxElementDescription(self.type_argument.name,
                                     self._type_element_description(), []),
        ]
        path_element = rel_path_doc.path_element_2(_REL_OPTION_CONFIG)
        all_elements = negation_elements + type_elements + [path_element]

        return all_elements

    def see_also_targets(self) -> list:
        return [
            syntax_elements.PATH_SYNTAX_ELEMENT.cross_reference_target,
        ]

    def _type_element_description(self):
        return (self._paragraphs(_TYPE_ELEMENT_DESCRIPTION_INTRO)
                +
                [transform_list_to_table(self._file_type_list())])

    def _file_type_list(self) -> lists.HeaderContentList:
        def type_description(file_type: file_properties.FileType) -> list:
            text = 'Tests if {PATH} is a {file_type}, or a {SYM_LNK} to a {file_type}.'
            if file_type is file_properties.FileType.SYMLINK:
                text = 'Tests if {PATH} is a {SYM_LNK} (link target may or may not exist).'
            extra = {
                'file_type': file_properties.TYPE_INFO[file_type].description,
            }
            return self._paragraphs(text, extra)

        sort_value__list_items = [
            (file_properties.TYPE_INFO[file_type],
             docs.list_item(syntax_text(render_argument(a.Option(option_name))),
                            type_description(file_type)))
            for file_type, option_name in FILE_TYPE_OPTIONS]
        sort_value__list_items.sort(key=lambda type_name__list_item: type_name__list_item[0].type_argument)
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
        tokens = TokenParserExtra(new_token_stream(rest_of_line),
                                  self.format_map)
        is_negated = tokens.consume_and_return_true_if_first_argument_is_unquoted_and_equals(NEGATION_OPERATOR)
        file_properties_check = tokens.consume_and_handle_first_matching_option(
            _DEFAULT_FILE_PROPERTIES_CHECK,
            _file_type_2_file_properties_check,
            FILE_TYPE_OPTIONS)
        if is_negated:
            file_properties_check = file_properties.negation_of(file_properties_check)
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


_TYPE_ELEMENT_DESCRIPTION_INTRO = """\
Includes the file type in the assertion.
"""

_PART_OF_MAIN_DESCRIPTION_REST_THAT_IS_SPECIFIC_FOR_THIS_INSTRUCTION = """\
If {TYPE} is not given, the type of the file is ignored.


When not negated, the assertion will
PASS if, and only if:

{PATH} exists, and is a file of the asserted type.


When negated, the assertion will
FAIL if, and only if:

{PATH} exists, and is a file of the asserted type.
"""
