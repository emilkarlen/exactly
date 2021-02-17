from exactly_lib.test_case.phases.act.execution_input import AtcExecutionInput
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


def for_atc(environment: InstructionEnvironmentForPostSdsStep,
            execution_input: AtcExecutionInput,
            ) -> ProcessExecutionSettings:
    return ProcessExecutionSettings(
        environment.proc_exe_settings.timeout_in_seconds,
        execution_input.environ,
    )
