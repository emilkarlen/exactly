from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.concepts.plain_concepts.current_working_directory import CURRENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.names import formatting
from exactly_lib.instructions.utils import file_properties
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.instructions.utils.file_ref_check import pre_or_post_sds_failure_message_or_none, FileRefCheck
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.section_document.parser_implementations.token_stream_parse import TokenParser
from exactly_lib.symbol.concrete_values import FileRefResolver
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render.cli_program_syntax import render_argument
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure import lists


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


TYPE_NAME_SYMLINK = 'symlink'
TYPE_NAME_REGULAR = 'regular'
TYPE_NAME_DIRECTORY = 'directory'

FILE_TYPE_OPTIONS = [
    (file_properties.FileType.SYMLINK, a.OptionName(long_name=TYPE_NAME_SYMLINK)),
    (file_properties.FileType.REGULAR, a.OptionName(long_name=TYPE_NAME_REGULAR)),
    (file_properties.FileType.DIRECTORY, a.OptionName(long_name=TYPE_NAME_DIRECTORY)),
]

_TYPE_ARGUMENT_STR = 'TYPE'

_PATH_ARGUMENT_STR = path_syntax.PATH_ARGUMENT


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        self.type_argument = a.Named(_TYPE_ARGUMENT_STR)
        self.path_argument = _PATH_ARGUMENT_STR
        super().__init__(name, {
            'PATH': self.path_argument.name,
            'cwd': formatting.concept(CURRENT_WORKING_DIRECTORY_CONCEPT.name().singular),
        })

    def single_line_description(self) -> str:
        return 'Tests the type of a file'

    def main_description_rest(self) -> list:
        text = """\
        PASS if, and only if, {PATH} exists, and is a file of the given type.


        {PATH} is relative the {cwd}.
        """
        return self._paragraphs(text)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.OPTIONAL,
                         self.type_argument),
                a.Single(a.Multiplicity.MANDATORY,
                         self.path_argument),
            ]),
                []),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(self.type_argument.name,
                                     [self._file_type_list()],
                                     [])
        ]

    def _see_also_cross_refs(self) -> list:
        return [
            CURRENT_WORKING_DIRECTORY_CONCEPT.cross_reference_target(),
        ]

    def _file_type_list(self) -> core.ParagraphItem:
        def type_description(file_type: file_properties.FileType) -> list:
            tn = file_properties.type_name[file_type]
            text = 'Tests if {PATH} is a %s, or a symbolic link to a %s.' % (tn, tn)
            if file_type is file_properties.FileType.SYMLINK:
                text = 'Tests if {PATH} is a %s.' % tn
            return self._paragraphs(text)

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
            'PATH': _PATH_ARGUMENT_STR,
        }

    def _parse(self, rest_of_line: str) -> AssertPhaseInstruction:
        tokens = TokenParser(TokenStream2(rest_of_line),
                             self.format_map)
        tokens.if_null_then_invalid_arguments('Missing {PATH} argument')
        file_properties_check = _parse_file_properties_check(tokens)
        file_name_argument = tokens.consume_mandatory_string_argument('Missing {PATH} argument')
        tokens.require_is_at_eol('Superfluous arguments')
        file_ref_resolver = FileRefConstant(file_refs.rel_cwd(PathPartAsFixedPath(file_name_argument)))
        return _Instruction(file_ref_resolver, file_properties_check)


def _parse_file_properties_check(tokens: TokenParser) -> file_properties.FilePropertiesCheck:
    ret_val = file_properties.must_exist(follow_symlinks=False)
    for file_type in tokens.consume_and_handle_first_matching_option(FILE_TYPE_OPTIONS):
        follow_sym_links = file_type is not file_properties.FileType.SYMLINK
        ret_val = file_properties.must_exist_as(file_type,
                                                follow_sym_links)
    return ret_val


class _Instruction(AssertPhaseInstruction):
    def __init__(self,
                 file_ref_resolver: FileRefResolver,
                 expected_file_properties: file_properties.FilePropertiesCheck):
        self._file_ref_resolver = file_ref_resolver
        self._expected_file_properties = expected_file_properties

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        failure_message = pre_or_post_sds_failure_message_or_none(
            FileRefCheck(self._file_ref_resolver,
                         self._expected_file_properties),
            environment.path_resolving_environment_pre_or_post_sds)
        if failure_message is not None:
            return pfh.new_pfh_fail(failure_message)
        return pfh.new_pfh_pass()
