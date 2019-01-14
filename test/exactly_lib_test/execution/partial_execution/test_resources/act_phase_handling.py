import sys

import pathlib
import subprocess

from exactly_lib.test_case.act_phase_handling import ActPhaseHandling, ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.util.std import StdFiles
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_source_and_executor_constructors import \
    ActionToCheckExecutorConstructorForConstantExecutor
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_source_and_executors import \
    ActionToCheckExecutorThatJustReturnsSuccess


class ExecutorThatExecutesPythonProgramSource(ActionToCheckExecutorThatJustReturnsSuccess):
    PYTHON_FILE_NAME = 'program.py'

    def __init__(self, python_program_source: str):
        self.python_program_source = python_program_source

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: ActPhaseOsProcessExecutor,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        python_file = pathlib.Path() / self.PYTHON_FILE_NAME
        with python_file.open(mode='w') as f:
            f.write(self.python_program_source)

        exit_code = subprocess.call([sys.executable, str(python_file)],
                                    timeout=60,
                                    stdin=std_files.stdin,
                                    stdout=std_files.output.out,
                                    stderr=std_files.output.err)
        return new_eh_exit_code(exit_code)


def act_phase_handling_for_execution_of_python_source(python_source: str) -> ActPhaseHandling:
    executor = ExecutorThatExecutesPythonProgramSource(python_source)
    parser = ActionToCheckExecutorConstructorForConstantExecutor(executor)
    return ActPhaseHandling(parser)
