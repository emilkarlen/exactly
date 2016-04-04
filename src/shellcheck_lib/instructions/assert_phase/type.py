from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InvokationVariant, \
    InstructionDocumentation, \
    SyntaxElementDescription
from shellcheck_lib.instructions.utils import file_ref
from shellcheck_lib.instructions.utils.file_properties import FileType, must_exist_as, FilePropertiesCheck, type_name
from shellcheck_lib.instructions.utils.file_ref_check import pre_or_post_eds_failure_message_or_none, FileRefCheck
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string, ensure_is_not_option_argument
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases import common as i
from shellcheck_lib.test_case.phases.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.phases.result import pfh
from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.structures import paras, text


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


FILE_TYPES = {
    "symlink": FileType.SYMLINK,
    "regular": FileType.REGULAR,
    "directory": FileType.DIRECTORY
}


class TheInstructionDocumentation(InstructionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Tests the type of a file.'

    def main_description_rest(self) -> list:
        return paras('All tests fails if FILENAME does not exist. (TODO symlink options/behavior)')

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                'FILENAME type TYPE',
                paras('File exists and has given type.')),
        ]

    def syntax_element_descriptions(self) -> list:
        def type_description(k: str) -> str:
            tn = type_name[FILE_TYPES[k]]
            return paras('Tests if FILENAME is a %s or, a sym-link to a %s.' % (tn, tn))

        def file_type_list() -> core.ParagraphItem:
            list_items = [
                lists.HeaderContentListItem(text(k),
                                            type_description(k))
                for k in sorted(FILE_TYPES.keys())]
            return lists.HeaderContentList(list_items,
                                           lists.Format(lists.ListType.VARIABLE_LIST))

        return [
            SyntaxElementDescription('TYPE',
                                     [file_type_list()],
                                     [])
        ]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        if len(arguments) != 2:
            raise SingleInstructionInvalidArgumentException('Invalid syntax')
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
            raise SingleInstructionInvalidArgumentException('Missing type argument')
        if num_arguments > 1:
            raise SingleInstructionInvalidArgumentException('Expecting a single type argument')
        try:
            file_type = FILE_TYPES[arguments[0]]
            follow_sym_links = file_type is not FileType.SYMLINK
            return must_exist_as(file_type,
                                 follow_sym_links)
        except KeyError:
            raise SingleInstructionInvalidArgumentException('Invalid file type: ' + arguments[0])


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
