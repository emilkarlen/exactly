from exactly_lib.definitions.entity import actors
from exactly_lib.impls.actors.program import actor as command_line_actor
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.phases.act.execution_input import AtcExecutionInput
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib_test.test_case.actor.test_resources.action_to_checks import \
    ActionToCheckThatRunsConstantActions
from exactly_lib_test.test_case.actor.test_resources.actor_impls import \
    ActorForConstantAtc


def act_setup_that_prints_single_string_on_stdout(string_to_print: str) -> ActPhaseSetup:
    return ActPhaseSetup(
        'actor for constant ATC',
        ActorForConstantAtc(
            ActionToCheckThatRunsConstantActions(
                execute_initial_action=PrintStringOnStdout(string_to_print)))
    )


def act_setup_that_does_nothing() -> ActPhaseSetup:
    return ActPhaseSetup(
        'actor that does nothing',
        ActorForConstantAtc(ActionToCheckThatRunsConstantActions()))


def command_line_actor_setup() -> ActPhaseSetup:
    return ActPhaseSetup(actors.COMMAND_LINE_ACTOR.singular_name,
                         command_line_actor.actor())


class PrintStringOnStdout:
    def __init__(self, string_to_print: str):
        self.string_to_print = string_to_print

    def __call__(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 atc_input: AtcExecutionInput,
                 output: StdOutputFiles):
        output.out.write(self.string_to_print)
