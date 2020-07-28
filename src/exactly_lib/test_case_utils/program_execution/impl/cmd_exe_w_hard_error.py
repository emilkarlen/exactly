from typing import Generic

from exactly_lib.common.report_rendering.parts.failure_details import FailureDetailsRenderer
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.exception_detection import DetectedException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case_utils.program import top_lvl_error_msg_rendering
from exactly_lib.test_case_utils.program_execution.command_processor import CommandProcessor, T
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.process_executor import ProcessExecutionException, ExecutableExecutor
from exactly_lib.util.simple_textstruct.rendering import line_objects, blocks


class Processor(Generic[T], CommandProcessor[T]):
    def __init__(self,
                 os_services: OsServices,
                 exe_of_executable: ExecutableExecutor[T],
                 ):
        self.os_services = os_services
        self.exe_of_executable = exe_of_executable

    def process(self,
                settings: ProcessExecutionSettings,
                command: Command,
                ) -> T:
        try:
            executable = self.os_services.executable_factory().make(command)
            return self.exe_of_executable.execute(settings, executable)
        except DetectedException as ex:
            raise HardErrorException(
                top_lvl_error_msg_rendering.unable_to_execute_msg(
                    command.structure().build(),
                    FailureDetailsRenderer(ex.failure_details))
            )
        except ProcessExecutionException as ex:
            raise HardErrorException(
                top_lvl_error_msg_rendering.unable_to_execute_msg(
                    command.structure().build(),
                    _string_major_blocks(str(ex.cause)))
            )


def _string_major_blocks(s: str) -> TextRenderer:
    return blocks.MajorBlocksOfSingleLineObject(
        line_objects.PreFormattedString.of_str(s)
    )
