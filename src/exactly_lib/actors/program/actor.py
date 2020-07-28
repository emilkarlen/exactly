from exactly_lib.actors.common import relativity_configuration_of_action_to_check
from exactly_lib.actors.program.executable_object import ProgramToExecute
from exactly_lib.actors.program.parse import Parser
from exactly_lib.actors.util.executor_made_of_parts import parts
from exactly_lib.definitions.test_case.actors import command_line as texts
from exactly_lib.symbol.sdv_validation import SdvValidatorFromDdvValidator
from exactly_lib.test_case.actor import AtcOsProcessExecutor, Actor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.util.symbol_table import SymbolTable
from . import execution
from ..util.executor_made_of_parts.parts import ValidatorFromPreOrPostSdsValidator


def actor() -> Actor:
    return parts.ActorFromParts(
        Parser(),
        _TheValidatorConstructor(),
        _TheExecutorConstructor(),
    )


RELATIVITY_CONFIGURATION = relativity_configuration_of_action_to_check(texts.EXECUTABLE)


class _TheValidatorConstructor(parts.ValidatorConstructor[ProgramToExecute]):
    def construct(self,
                  environment: InstructionEnvironmentForPreSdsStep,
                  executable_object: ProgramToExecute,
                  ) -> parts.Validator:
        def get_validator(symbols: SymbolTable) -> DdvValidator:
            return ddv_validators.all_of(executable_object.program.resolve(symbols).validators)

        return ValidatorFromPreOrPostSdsValidator(
            SdvValidatorFromDdvValidator(get_validator)
        )


class _TheExecutorConstructor(parts.ExecutorConstructor[ProgramToExecute]):
    def construct(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  os_process_executor: AtcOsProcessExecutor,
                  executable_object: ProgramToExecute,
                  ) -> parts.Executor:
        return execution.Executor(os_services,
                                  os_process_executor,
                                  executable_object.program)