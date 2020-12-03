from typing import Callable, Optional

from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.std import StdOutputFiles

BeforeExecuteMethod = Callable[
    [InstructionEnvironmentForPostSdsStep, Optional[StringSource], StdOutputFiles],
    None]

ExecuteFunctionEh = Callable[
    [InstructionEnvironmentForPostSdsStep, Optional[StringSource], StdOutputFiles],
    ExitCodeOrHardError]

ExecuteFunction = Callable[
    [InstructionEnvironmentForPostSdsStep, Optional[StringSource], StdOutputFiles],
    int]
