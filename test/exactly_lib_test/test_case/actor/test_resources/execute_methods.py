from typing import Callable

from exactly_lib.test_case.phases.act.execution_input import ActExecutionInput
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.util.file_utils.std import StdOutputFiles

BeforeExecuteMethod = Callable[
    [InstructionEnvironmentForPostSdsStep, ActExecutionInput, StdOutputFiles],
    None]

ExecuteFunctionEh = Callable[
    [InstructionEnvironmentForPostSdsStep, ActExecutionInput, StdOutputFiles],
    ExitCodeOrHardError]

ExecuteFunction = Callable[
    [InstructionEnvironmentForPostSdsStep, ActExecutionInput, StdOutputFiles],
    int]
