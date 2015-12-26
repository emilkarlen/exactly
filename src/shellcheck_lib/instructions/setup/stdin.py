from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.general.string import lines_content
from shellcheck_lib.general.textformat.structure.paragraph import single_para
from shellcheck_lib.instructions.setup.utils.instruction_utils import InstructionWithFileRefsBase
from shellcheck_lib.instructions.utils import file_properties
from shellcheck_lib.instructions.utils import file_ref, parse_file_ref
from shellcheck_lib.instructions.utils import parse_here_doc_or_file_ref
from shellcheck_lib.instructions.utils.file_properties import FileType
from shellcheck_lib.instructions.utils.file_ref_check import FileRefCheck
from shellcheck_lib.instructions.utils.parse_utils import spit_arguments_list_string
from shellcheck_lib.test_case.help.instruction_description import InvokationVariant, Description
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


class TheDescription(Description):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Redirects stdin, for the act program, to a given file, or string.'

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    '[{}] FILE'.format('|'.join(parse_file_ref.ALL_REL_OPTIONS)),
                    single_para('Sets stdin to a file relative SHELLCHECK_HOME.')),
            InvokationVariant(
                    '<<EOF-MARKER'.format('|'.join(parse_file_ref.ALL_REL_OPTIONS)),
                    single_para('Sets stdin to the contents of the given Here Document.')),
        ]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        first_line_arguments = spit_arguments_list_string(source.instruction_argument)
        if not first_line_arguments:
            raise SingleInstructionInvalidArgumentException('Missing arguments: no arguments')
        (here_doc_or_file_ref, remaining_arguments) = parse_here_doc_or_file_ref.parse(first_line_arguments, source)
        if remaining_arguments:
            raise SingleInstructionInvalidArgumentException('Superfluous arguments: ' + str(remaining_arguments))
        if here_doc_or_file_ref.is_here_document:
            content = lines_content(here_doc_or_file_ref.here_document)
            return _InstructionForHereDocument(content)
        return _InstructionForFileRef(here_doc_or_file_ref.file_reference)


class _InstructionForHereDocument(SetupPhaseInstruction):
    def __init__(self, contents: str):
        self.contents = contents

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        settings_builder.stdin.contents = self.contents
        return sh.new_sh_success()


class _InstructionForFileRef(InstructionWithFileRefsBase):
    def __init__(self, redirect_file: file_ref.FileRef):
        super().__init__((FileRefCheck(redirect_file,
                                       file_properties.must_exist_as(FileType.REGULAR)),))
        self.redirect_file = redirect_file

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        settings_builder.stdin.file_name = str(self.redirect_file.file_path_pre_or_post_eds(environment.home_and_eds))
        return sh.new_sh_success()
