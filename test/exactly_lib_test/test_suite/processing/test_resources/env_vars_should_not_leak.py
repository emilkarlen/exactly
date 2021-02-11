from typing import List

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.instruction import SetupPhaseInstruction
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.test_case.result import sh
from exactly_lib_test.test_suite.processing.test_resources.instruction_utils import InstructionParserBase


class Registry:
    def __init__(self):
        self.observation = None


class SetupPhaseInstructionThatSetsEnvVar(SetupPhaseInstruction):
    def __init__(self,
                 var_name: str,
                 var_value: str):
        self.var_name = var_name
        self.var_value = var_value

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        environment.proc_exe_settings.environ[self.var_name] = self.var_value
        return sh.new_sh_success()


class SetupPhaseInstructionThatRegistersExistenceOfEnvVar(SetupPhaseInstruction):
    def __init__(self,
                 registry: Registry,
                 env_var_to_observe: str):
        self.registry = registry
        self.env_var_to_observe = env_var_to_observe

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        self.registry.observation = self.env_var_to_observe in environment.proc_exe_settings.environ
        return sh.new_sh_success()


class InstructionParserForSet(InstructionParserBase):
    def __init__(self):
        super().__init__(3)

    def _parse(self, args: List[str]) -> SetupPhaseInstruction:
        return SetupPhaseInstructionThatSetsEnvVar(var_name=args[0],
                                                   var_value=args[2])


class InstructionParserForRegistersExistenceOfEnvVar(InstructionParserBase):
    def __init__(self, registry: Registry):
        super().__init__(1)
        self.registry = registry

    def _parse(self, args: List[str]) -> SetupPhaseInstruction:
        return SetupPhaseInstructionThatRegistersExistenceOfEnvVar(self.registry,
                                                                   args[0])
