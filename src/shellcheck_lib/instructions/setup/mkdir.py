import pathlib

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils.parse_utils import spit_arguments_list_string, ensure_is_not_option_argument
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib.test_case.os_services import OsServices

DESCRIPTION = Description(
    'Makes a directory in the current directory',
    """
    Makes parent components, if needed.


    Does not fail if the given directory already exists.
    """,
    [InvokationVariant('DIRECTORY',
                       ''),
     ])


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        arguments = spit_arguments_list_string(source.instruction_argument)
        if len(arguments) != 1:
            raise SingleInstructionInvalidArgumentException('Usage: DIRECTORY')
        argument = arguments[0]
        ensure_is_not_option_argument(argument)
        return _Instruction(argument)


class _Instruction(SetupPhaseInstruction):
    def __init__(self, directory_components: str):
        self.directory_components = directory_components

    def pre_validate(self,
                     global_environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        dir_path = pathlib.Path() / self.directory_components
        if dir_path.is_dir():
            return sh.new_sh_success()
        try:
            dir_path.mkdir(parents=True)
        except FileExistsError:
            return sh.new_sh_hard_error('Path exists, but is not a directory: {}'.format(dir_path))
        except NotADirectoryError:
            return sh.new_sh_hard_error('Clash with existing file: {}'.format(dir_path))
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()
