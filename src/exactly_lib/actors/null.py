from typing import Sequence

from exactly_lib.actors.util.actor_from_parts import parts
from exactly_lib.actors.util.actor_from_parts.parts import ExecutableObjectParser
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import SymbolUser
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.util.file_utils.std import StdFiles


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
                std_files: StdFiles,
                ) -> int:
        return 0


class _ExecutorConstructor(parts.ExecutorConstructor[_ObjectToExecute]):
    def construct(self,
                  environment: InstructionEnvironmentForPreSdsStep,
                  os_services: OsServices,
                  object_to_execute: _ObjectToExecute) -> parts.Executor:
        return _Executor()
