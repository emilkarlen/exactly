import pathlib
import shutil
import subprocess

from exactly_lib.test_case import exception_detection
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.test_case.eh import ExitCodeOrHardError, new_eh_exit_code, new_eh_hard_error
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.failure_details import new_failure_details_from_exception, FailureDetails
from exactly_lib.util.process_execution.os_process_execution import Command, ProcessExecutionSettings
from exactly_lib.util.std import StdFiles


class OsServices:
    """
    Interface to some Operation System Services.

    These are services that should not be implemented as part of instructions, and
    that may vary depending on operating system.
    """

    def make_dir_if_not_exists__detect_ex(self, path: pathlib.Path):
        """
        :raises DetectedException
        """
        raise NotImplementedError()

    def copy_file_preserve_as_much_as_possible__detect_ex(self, src: str, dst: str):
        """
        :raises DetectedException
        """
        raise NotImplementedError()

    def copy_tree_preserve_as_much_as_possible__detect_ex(self, src: str, dst: str):
        """
        :raises DetectedException
        """
        raise NotImplementedError()

    def copy_file_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        return exception_detection.return_success_or_hard_error(
            self.copy_file_preserve_as_much_as_possible__detect_ex,
            src, dst)

    def copy_tree_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        return exception_detection.return_success_or_hard_error(
            self.copy_tree_preserve_as_much_as_possible__detect_ex,
            src, dst)


def new_default() -> OsServices:
    return _Default()


def new_with_environ() -> OsServices:
    return _Default()


class _Default(OsServices):
    def make_dir_if_not_exists__detect_ex(self, path: pathlib.Path):
        try:
            path.mkdir(parents=True, exist_ok=True)
        except FileExistsError as ex:
            _raise_fail_to_make_dir_exception(path, ex)
        except OSError as ex:
            _raise_fail_to_make_dir_exception(path, ex)

    def copy_file_preserve_as_much_as_possible__detect_ex(self, src: str, dst: str):
        try:
            shutil.copy2(src, dst)
        except OSError as ex:
            raise exception_detection.DetectedException(
                FailureDetails('Failed to copy file {} -> {}:\n{}'.format(src, dst, str(ex)),
                               ex))

    def copy_tree_preserve_as_much_as_possible__detect_ex(self, src: str, dst: str):
        try:
            shutil.copytree(src, dst)
        except OSError as ex:
            raise exception_detection.DetectedException(
                FailureDetails('Failed to copy tree {} -> {}:\n{}'.format(src, dst, str(ex)),
                               ex))


class ActPhaseSubProcessExecutor(ActPhaseOsProcessExecutor):
    def execute(self,
                command: Command,
                std_files: StdFiles,
                process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
        try:
            exit_code = subprocess.call(command.args,
                                        timeout=process_execution_settings.timeout_in_seconds,
                                        env=process_execution_settings.environ,
                                        shell=command.shell,
                                        stdin=std_files.stdin,
                                        stdout=std_files.output.out,
                                        stderr=std_files.output.err)
            return new_eh_exit_code(exit_code)
        except ValueError as ex:
            return self._exception(ex)
        except OSError as ex:
            return self._exception(ex)
        except subprocess.TimeoutExpired as ex:
            return self._exception(ex)

    @staticmethod
    def _exception(ex: Exception) -> ExitCodeOrHardError:
        msg = 'Error executing act program in sub process.'
        return new_eh_hard_error(new_failure_details_from_exception(ex, message=msg))


ACT_PHASE_OS_PROCESS_EXECUTOR = ActPhaseSubProcessExecutor()


def _raise_fail_to_make_dir_exception(path: pathlib.Path, ex: Exception):
    raise exception_detection.DetectedException(
        FailureDetails('Failed to make directory {}:\n{}'.format(path, str(ex)),
                       ex))
