from exactly_lib.common.instruction_documentation import InvokationVariant, \
    SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.concepts.plain_concepts.present_working_directory import PRESENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.utils import file_ref
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string, \
    ensure_is_not_option_argument
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.instructions.utils.file_properties import FileType, must_exist_as, FilePropertiesCheck, type_name
from exactly_lib.instructions.utils.file_ref_check import pre_or_post_eds_failure_message_or_none, FileRefCheck
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure import lists


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


FILE_TYPES = {
    "symlink": FileType.SYMLINK,
    "regular": FileType.REGULAR,
    "directory": FileType.DIRECTORY
}

_TYPE_ARGUMENT_STR = 'TYPE'


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        self.type_argument = a.Named(_TYPE_ARGUMENT_STR)
        self.path_argument = dt.PATH_ARGUMENT
        super().__init__(name, {
            'PATH': self.path_argument.name,
            'pwd': formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT.name().singular),
        })

    def single_line_description(self) -> str:
        return 'Tests the type of a file.'

    def main_description_rest(self) -> list:
        text = """\
        PASS if, and only if, {PATH} exists, and is a file of the given type.


        {PATH} is relative the {pwd}.
        """
        return self._paragraphs(text)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY,
                         self.path_argument),
                a.Single(a.Multiplicity.MANDATORY,
                         self.type_argument),
            ]),
                []),
        ]

    def syntax_element_descriptions(self) -> list:
        def type_description(k: str) -> str:
            tn = type_name[FILE_TYPES[k]]
            text = 'Tests if {PATH} is a %s, or a symbolic link to a %s.' % (tn, tn)
            if FILE_TYPES[k] is FileType.SYMLINK:
                text = 'Tests if {PATH} is a %s.' % tn
            return self._paragraphs(text)

        def file_type_list() -> core.ParagraphItem:
            list_items = [
                lists.HeaderContentListItem(self._text(k),
                                            type_description(k))
                for k in sorted(FILE_TYPES.keys())]
            return lists.HeaderContentList(list_items,
                                           lists.Format(lists.ListType.VARIABLE_LIST))

        return [
            SyntaxElementDescription(self.type_argument.name,
                                     [file_type_list()],
                                     [])
        ]

    def see_also(self) -> list:
        return [
            PRESENT_WORKING_DIRECTORY_CONCEPT.cross_reference_target(),
        ]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        if len(arguments) != 2:
            raise SingleInstructionInvalidArgumentException('Expecting exactly two arguments.')
        file_argument = arguments[0]
        ensure_is_not_option_argument(file_argument)
        file_reference = file_ref.rel_cwd(file_argument)
        del arguments[0]
        expected_properties = self._parse_properties(arguments)
        return _Instruction(file_reference, expected_properties)

    @staticmethod
    def _parse_properties(arguments: list) -> FilePropertiesCheck:
        num_arguments = len(arguments)
        if num_arguments == 0:
            msg = 'Missing {TYPE} argument.'.format(TYPE=_TYPE_ARGUMENT_STR)
            raise SingleInstructionInvalidArgumentException(msg)
        if num_arguments > 1:
            msg = 'Expecting a single {TYPE} argument.'.format(TYPE=_TYPE_ARGUMENT_STR)
            raise SingleInstructionInvalidArgumentException(msg)
        try:
            file_type = FILE_TYPES[arguments[0]]
            follow_sym_links = file_type is not FileType.SYMLINK
            return must_exist_as(file_type,
                                 follow_sym_links)
        except KeyError:
            msg = 'Invalid {TYPE}: "{arg}".'.format(TYPE=_TYPE_ARGUMENT_STR, arg=arguments[0])
            raise SingleInstructionInvalidArgumentException(msg)


class _Instruction(AssertPhaseInstruction):
    def __init__(self,
                 file_reference: file_ref.FileRef,
                 expected_file_properties: FilePropertiesCheck):
        self._file_reference = file_reference
        self._expected_file_properties = expected_file_properties

    def main(self,
             environment: i.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        failure_message = pre_or_post_eds_failure_message_or_none(FileRefCheck(self._file_reference,
                                                                               self._expected_file_properties),
                                                                  environment.home_and_eds)
        if failure_message is not None:
            return pfh.new_pfh_fail(failure_message)
        return pfh.new_pfh_pass()
