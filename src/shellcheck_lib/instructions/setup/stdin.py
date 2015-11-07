from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.setup.utils.instruction_utils import InstructionWithFileRefsBase
from shellcheck_lib.instructions.utils import file_ref, parse_file_ref
from shellcheck_lib.instructions.utils.parse_utils import spit_arguments_list_string
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib.test_case.os_services import OsServices

DESCRIPTION = Description(
    'Redirects stdin, for the act program, to a given file.',
    '',
    [InvokationVariant('[--rel-home|rel-tmp|rel-cwd] FILE',
                       'Sets stdin to a file relative SHELLCHECK_HOME.'),
     ])


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        arguments = spit_arguments_list_string(source.instruction_argument)
        (file_reference, remaining_arguments) = parse_file_ref.parse_non_act_generated_file(arguments)
        if remaining_arguments:
            raise SingleInstructionInvalidArgumentException('Superfluous arguments: ' + str(remaining_arguments))
        return _Instruction(file_reference)


class _Instruction(InstructionWithFileRefsBase):
    def __init__(self, redirect_file: file_ref.FileRef):
        super().__init__((redirect_file,))
        self.redirect_file = redirect_file

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        settings_builder.set_stdin_file(str(self.redirect_file.file_path(environment)))
        return sh.new_sh_success()
