import pathlib
import subprocess
import sys
from typing import Optional

from exactly_lib.impls.types.string_model import as_stdin
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib_test.test_case.actor.test_resources.action_to_checks import \
    ActionToCheckThatJustReturnsSuccess
from exactly_lib_test.test_case.actor.test_resources.actor_impls import \
    ActorForConstantAtc


class AtcThatExecutesPythonProgramSource(ActionToCheckThatJustReturnsSuccess):
    PYTHON_FILE_NAME = 'logic_symbol_utils.py'

    def __init__(self, python_program_source: str):
        self.python_program_source = python_program_source

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                stdin: Optional[StringModel],
                output: StdOutputFiles,
                ) -> ExitCodeOrHardError:
        python_file = pathlib.Path() / self.PYTHON_FILE_NAME
        with python_file.open(mode='w') as f:
            f.write(self.python_program_source)
        with as_stdin.of_optional(stdin) as stdin_f:
            exit_code = subprocess.call([sys.executable, str(python_file)],
                                        timeout=60,
                                        stdin=stdin_f,
                                        stdout=output.out,
                                        stderr=output.err)
        return new_eh_exit_code(exit_code)


def actor_for_execution_of_python_source(python_source: str) -> Actor:
    atc = AtcThatExecutesPythonProgramSource(python_source)
    return ActorForConstantAtc(atc)
