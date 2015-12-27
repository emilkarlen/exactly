from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.general.textformat.structure.paragraph import single_para
from shellcheck_lib.instructions.utils.parse_utils import spit_arguments_list_string
from shellcheck_lib.test_case.instruction_description import InvokationVariant, Description
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


class TheDescription(Description):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Manipulates environment variables.'

    def main_description_rest(self) -> list:
        return []

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    'NAME = VALUE',
                    single_para('Sets the environment variable NAME to VALUE.')),
            InvokationVariant(
                    'unset NAME',
                    single_para('Removes the environment variable NAME.')),
        ]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        arguments = spit_arguments_list_string(source.instruction_argument)
        if len(arguments) == 3 and arguments[1] == '=':
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
