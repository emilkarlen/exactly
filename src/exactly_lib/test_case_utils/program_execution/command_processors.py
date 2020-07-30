from pathlib import Path
from typing import TypeVar, Callable

from exactly_lib.common.err_msg import std_err_contents
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case_utils.program_execution.command_processor import CommandProcessor
from exactly_lib.util.file_utils.std import StdFiles

T = TypeVar('T')


def processor__raw(
        os_services: OsServices,
        files: StdFiles,
) -> CommandProcessor[int]:
    from exactly_lib.util.process_execution.executors.executor import ProcessorFromExecutor
    return ProcessorFromExecutor(
        os_services.command_executor,
        files
    )


def processor_that_raises_hard_error_on_non_zero_exit_code(
        exit_code_agnostic_processor_w_hard_error: CommandProcessor[T],
        get_exit_code: Callable[[T], int],
        get_stderr: Callable[[T], Path],
) -> CommandProcessor[T]:
    from .impl import cmd_proc_w_exit_code_handling
    return cmd_proc_w_exit_code_handling.Processor(
        std_err_contents.STD_ERR_TEXT_READER,
        get_exit_code,
        get_stderr,
        exit_code_agnostic_processor_w_hard_error,
    )


def processor_that_optionally_raises_hard_error_on_non_zero_exit_code(
        ignore_non_zero_exit_code: bool,
        exit_code_agnostic_processor_w_hard_error: CommandProcessor[T],
        get_exit_code: Callable[[T], int],
        get_stderr: Callable[[T], Path],
) -> CommandProcessor[T]:
    return (
        exit_code_agnostic_processor_w_hard_error
        if ignore_non_zero_exit_code
        else
        processor_that_raises_hard_error_on_non_zero_exit_code(
            exit_code_agnostic_processor_w_hard_error,
            get_exit_code,
            get_stderr,
        )
    )
