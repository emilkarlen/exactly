import shlex

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib.test_case.os_services import OsServices

DESCRIPTION = Description(
    'Manipulates environment variables.',
    '',
    [InvokationVariant('NAME = VALUE',
                       'Sets the environment variable NAME to VALUE.'),
     InvokationVariant('unset NAME',
                       'Removes the environment variable NAME.'),
     ])


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        arguments = shlex.split(source.instruction_argument)
        if len(arguments) == 3 and arguments[1] != '=':
            return _SetInstruction(arguments[0], arguments[2])
        if len(arguments) == 2 and arguments[0] == 'unset':
            return _UnsetInstruction(arguments[1])
        raise SingleInstructionInvalidArgumentException('Invalid syntax')


class _InstructionBase(SetupPhaseInstruction):
    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        raise NotImplementedError()

    def pre_validate(self, environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def post_validate(self,
                      environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class _SetInstruction(_InstructionBase):
    def __init__(self,
                 name: str,
                 value: str):
        self.name = name
        self.value = value

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        os_services.environ[self.name] = self.value
        return sh.new_sh_success()


class _UnsetInstruction(_InstructionBase):
    def __init__(self,
                 name: str):
        self.name = name

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        del os_services.environ[self.name]
        return sh.new_sh_success()
