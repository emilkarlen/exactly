from typing import Dict, List

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutFileReferenceRelativityRoot, InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case.result import sh
from exactly_lib_test.common.test_resources.instruction_documentation import instruction_documentation


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
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        environment.environ[self.var_name] = self.var_value
        return sh.new_sh_success()


class SetupPhaseInstructionThatRegistersExistenceOfEnvVar(SetupPhaseInstruction):
    def __init__(self,
                 registry: Registry,
                 env_var_to_observe: str):
        self.registry = registry
        self.env_var_to_observe = env_var_to_observe

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        self.registry.observation = self.env_var_to_observe in environment.environ
        return sh.new_sh_success()


class SetupPhaseInstructionThatAbortsIfEnvVarExists(SetupPhaseInstruction):
    def __init__(self, env_var_to_observe: str):
        self.env_var_to_observe = env_var_to_observe

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        if self.env_var_to_observe in environment.environ:
            return sh.new_sh_hard_error('Observed env var in environment: change name of it or '
                                        'somehow get rid of the var from the environment')
        return sh.new_sh_success()


class InstructionParserBase(InstructionParserWithoutFileReferenceRelativityRoot):
    def __init__(self, num_args: int):
        self.num_args = num_args

    def parse_from_source(self, source: ParseSource) -> SetupPhaseInstruction:
        args = source.remaining_part_of_current_line
        source.consume_current_line()
        components = args.split()
        if len(components) != self.num_args:
            raise ValueError('Expecting {} args. Found {} args'.format(self.num_args, len(components)))
        return self._parse(components)

    def _parse(self, args: List[str]) -> SetupPhaseInstruction:
        raise NotImplementedError('abstract method')


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


class InstructionParserForAbortsIfEnvVarExists(InstructionParserBase):
    def __init__(self):
        super().__init__(1)

    def _parse(self, args: List[str]) -> SetupPhaseInstruction:
        return SetupPhaseInstructionThatAbortsIfEnvVarExists(args[0])


def instruction_setup(setup_phase_instructions: Dict[str, InstructionParser]) -> InstructionsSetup:
    return InstructionsSetup({},
                             {name: SingleInstructionSetup(parser,
                                                           instruction_documentation('name-of-instruction'))
                              for name, parser in setup_phase_instructions.items()},
                             {}, {}, {})
