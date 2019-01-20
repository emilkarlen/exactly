import pathlib

from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.std import StdFiles
from exactly_lib_test.test_case.actor.test_resources.act_source_and_executors import \
    ActionToCheckExecutorThatRunsConstantActions
from exactly_lib_test.test_case.actor.test_resources.actor_impls import \
    ActorForConstantExecutor


def act_setup_that_prints_single_string_on_stdout(string_to_print: str) -> ActPhaseSetup:
    return ActPhaseSetup(ActorForConstantExecutor(
        ActionToCheckExecutorThatRunsConstantActions(
            execute_initial_action=PrintStringOnStdout(string_to_print)))
    )


def act_setup_that_does_nothing() -> ActPhaseSetup:
    return ActPhaseSetup(ActorForConstantExecutor(
        ActionToCheckExecutorThatRunsConstantActions())
    )


class PrintStringOnStdout:
    def __init__(self, string_to_print: str):
        self.string_to_print = string_to_print

    def __call__(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 script_output_dir_path: pathlib.Path,
                 std_files: StdFiles):
        std_files.output.out.write(self.string_to_print)
