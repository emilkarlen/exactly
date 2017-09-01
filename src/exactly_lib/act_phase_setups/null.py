import pathlib

from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parts import Parser, UnconditionallySuccessfulValidator
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case import eh
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor, ActPhaseHandling
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, SymbolUser
from exactly_lib.util.std import StdFiles


def act_phase_setup() -> ActPhaseSetup:
    return ActPhaseSetup(Constructor())


def act_phase_handling() -> ActPhaseHandling:
    return ActPhaseHandling(Constructor())


class _ObjectToExecute(SymbolUser):
    pass


class Constructor(parts.Constructor):
    def __init__(self):
        super().__init__(_Parser(),
                         UnconditionallySuccessfulValidator,
                         _executor_constructor)


class _Parser(Parser):
    def apply(self, act_phase_instructions: list) -> _ObjectToExecute:
        return _ObjectToExecute()


class _Executor(parts.Executor):
    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> eh.ExitCodeOrHardError:
        return eh.new_eh_exit_code(0)


def _executor_constructor(os_process_executor: ActPhaseOsProcessExecutor,
                          environment: InstructionEnvironmentForPreSdsStep,
                          object_to_execute: _ObjectToExecute) -> parts.Executor:
    return _Executor()
