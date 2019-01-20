import sys

import pathlib
import subprocess

from exactly_lib.test_case.actor import ActPhaseOsProcessExecutor, Actor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.util.std import StdFiles
from exactly_lib_test.test_case.actor.test_resources.act_source_and_executors import \
    ActionToCheckThatJustReturnsSuccess
from exactly_lib_test.test_case.actor.test_resources.actor_impls import \
    ActorForConstantAtc


class AtcThatExecutesPythonProgramSource(ActionToCheckThatJustReturnsSuccess):
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


def actor_for_execution_of_python_source(python_source: str) -> Actor:
    atc = AtcThatExecutesPythonProgramSource(python_source)
    return ActorForConstantAtc(atc)
