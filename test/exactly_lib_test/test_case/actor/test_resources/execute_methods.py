from typing import Callable

from exactly_lib.test_case.phases.act.execution_input import AtcExecutionInput
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.util.file_utils.std import StdOutputFiles

BeforeExecuteMethod = Callable[
    [InstructionEnvironmentForPostSdsStep, AtcExecutionInput, StdOutputFiles],
    None]

ExecuteFunctionEh = Callable[
    [InstructionEnvironmentForPostSdsStep, AtcExecutionInput, StdOutputFiles],
    ExitCodeOrHardError]

ExecuteFunction = Callable[
    [InstructionEnvironmentForPostSdsStep, AtcExecutionInput, StdOutputFiles],
    int]
