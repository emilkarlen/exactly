from exactly_lib.act_phase_setups.source_interpreter import executable_file
from exactly_lib.act_phase_setups.source_interpreter import shell_command as shell_cmd
from exactly_lib.act_phase_setups.source_interpreter.source_file_management import SourceInterpreterSetup, \
    StandardSourceFileManager
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling, ActSourceAndExecutorConstructor
from exactly_lib.util.process_execution.os_process_execution import Command


def act_phase_handling(command: Command) -> ActPhaseHandling:
    return ActPhaseHandling(act_source_and_executor_constructor(command))


def act_phase_setup(command: Command) -> ActPhaseSetup:
    return ActPhaseSetup(act_source_and_executor_constructor(command))


def act_source_and_executor_constructor(command: Command) -> ActSourceAndExecutorConstructor:
    if command.shell:
        return shell_cmd.Constructor(command.args)
    else:
        return executable_file.Constructor(
            SourceInterpreterSetup(StandardSourceFileManager(
                'src',
                command.args[0],
                command.args[1:])))
