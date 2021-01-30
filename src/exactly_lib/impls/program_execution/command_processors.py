from pathlib import Path
from typing import TypeVar, Callable

from exactly_lib.common.err_msg import std_err_contents
from exactly_lib.impls.program_execution.command_processor import CommandProcessor

T = TypeVar('T')


def processor_that_raises_hard_error_on_non_zero_exit_code(
        exit_code_agnostic_processor_w_hard_error: CommandProcessor[T],
        get_exit_code: Callable[[T], int],
        get_stderr: Callable[[T], Path],
) -> CommandProcessor[T]:
    from .processors import w_exit_code_handling
    return w_exit_code_handling.Processor(
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
