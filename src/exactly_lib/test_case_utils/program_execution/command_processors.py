from pathlib import Path
from typing import TypeVar, Callable

from exactly_lib.common.err_msg import std_err_contents
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case_utils.program_execution.command_processor import CommandProcessor
from exactly_lib.util.process_execution.process_executor import ExecutableExecutor

T = TypeVar('T')


def processor_that_raises_hard_error(
        os_services: OsServices,
        exe_of_executable: ExecutableExecutor[T]
) -> CommandProcessor[T]:
    from .impl import cmd_exe_w_hard_error
    return cmd_exe_w_hard_error.Processor(
        os_services,
        exe_of_executable,
    )


def processor_that_raises_hard_error_on_non_zero_exit_code(
        os_services: OsServices,
        exe_of_executable: ExecutableExecutor[T],
        get_exit_code: Callable[[T], int],
        get_stderr: Callable[[T], Path],
) -> CommandProcessor[T]:
    from .impl import cmd_executor_w_exit_code_handling
    return cmd_executor_w_exit_code_handling.Processor(
        std_err_contents.STD_ERR_TEXT_READER,
        get_exit_code,
        get_stderr,
        processor_that_raises_hard_error(os_services,
                                         exe_of_executable),
    )


def processor_that_raises_hard_error_on_non_zero_exit_code__command(
        exit_code_agnostic_processor_w_hard_error: CommandProcessor[T],
        get_exit_code: Callable[[T], int],
        get_stderr: Callable[[T], Path],
) -> CommandProcessor[T]:
    from .impl import cmd_executor_w_exit_code_handling
    return cmd_executor_w_exit_code_handling.Processor(
        std_err_contents.STD_ERR_TEXT_READER,
        get_exit_code,
        get_stderr,
        exit_code_agnostic_processor_w_hard_error,
    )


def processor_that_optionally_raises_hard_error_on_non_zero_exit_code(
        ignore_non_zero_exit_code: bool,
        os_services: OsServices,
        exe_of_executable: ExecutableExecutor[T],
        get_exit_code: Callable[[T], int],
        get_stderr: Callable[[T], Path],
) -> CommandProcessor[T]:
    return (
        processor_that_raises_hard_error(
            os_services,
            exe_of_executable,
        )
        if ignore_non_zero_exit_code
        else
        processor_that_raises_hard_error_on_non_zero_exit_code(
            os_services,
            exe_of_executable,
            get_exit_code,
            get_stderr,
        )
    )


def processor_that_optionally_raises_hard_error_on_non_zero_exit_code__command(
        ignore_non_zero_exit_code: bool,
        exit_code_agnostic_processor_w_hard_error: CommandProcessor[T],
        get_exit_code: Callable[[T], int],
        get_stderr: Callable[[T], Path],
) -> CommandProcessor[T]:
    return (
        exit_code_agnostic_processor_w_hard_error
        if ignore_non_zero_exit_code
        else
        processor_that_raises_hard_error_on_non_zero_exit_code__command(
            exit_code_agnostic_processor_w_hard_error,
            get_exit_code,
            get_stderr,
        )
    )
