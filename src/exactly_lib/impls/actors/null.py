from typing import Sequence, Optional

from exactly_lib.impls.actors.util.actor_from_parts import parts
from exactly_lib.impls.actors.util.actor_from_parts.parts import ExecutableObjectParser
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.common import SymbolUser
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


def actor() -> Actor:
    return parts.ActorFromParts(
        _Parser(),
        parts.UnconditionallySuccessfulValidatorConstructor(),
        _ExecutorConstructor(),
    )


class _ObjectToExecute(SymbolUser):
    pass


class _Parser(ExecutableObjectParser):
    def apply(self, instructions: Sequence[ActPhaseInstruction]) -> _ObjectToExecute:
        return _ObjectToExecute()


class _Executor(parts.Executor):
    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                settings: ProcessExecutionSettings,
                stdin: Optional[StringSource],
                output: StdOutputFiles,
                ) -> int:
        return 0


class _ExecutorConstructor(parts.ExecutorConstructor[_ObjectToExecute]):
    def construct(self,
                  environment: InstructionEnvironmentForPreSdsStep,
                  os_services: OsServices,
                  object_to_execute: _ObjectToExecute) -> parts.Executor:
        return _Executor()
