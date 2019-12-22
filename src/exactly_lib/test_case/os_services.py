import os
import pathlib
import shutil
import subprocess

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.definitions.entity import concepts
from exactly_lib.test_case import exception_detection, executable_factories
from exactly_lib.test_case.actor import AtcOsProcessExecutor
from exactly_lib.test_case.executable_factory import ExecutableFactory
from exactly_lib.test_case.result import sh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code, new_eh_hard_error
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util import strings
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
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

    def executable_factory__detect_ex(self) -> ExecutableFactory:
        """
        :raises DetectedException
        """
        raise NotImplementedError('abstract method')


def new_default() -> OsServices:
    return _Default()


def new_with_environ() -> OsServices:
    return _Default()


class _Default(OsServices):
    def __init__(self):
        try:
            self._executable_factory = executable_factories.get_factory_for_operating_system(os.name)
            self._platform_system_not_supported = None
        except KeyError:
            self._platform_system_not_supported = 'System not supported: ' + os.name

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
                FailureDetails.new_message(
                    text_docs.single_line(
                        strings.FormatMap(
                            'Failed to copy file {src} -> {dst}',
                            {'src': src,
                             'dst': dst
                             })
                    ),
                    ex)
            )

    def copy_tree_preserve_as_much_as_possible__detect_ex(self, src: str, dst: str):
        try:
            shutil.copytree(src, dst)
        except OSError as ex:
            raise exception_detection.DetectedException(
                FailureDetails.new_message(
                    text_docs.single_line(
                        strings.FormatMap('Failed to copy tree {src} -> {dst}',
                                          {'src': src,
                                           'dst': dst})
                    ),
                    ex
                ))

    def executable_factory__detect_ex(self) -> ExecutableFactory:
        if self._platform_system_not_supported:
            raise exception_detection.DetectedException(
                FailureDetails.new_constant_message(self._platform_system_not_supported)
            )
        return self._executable_factory


class AtcSubProcessExecutor(AtcOsProcessExecutor):
    def __init__(self, executable_factory: ExecutableFactory):
        self._executable_factory = executable_factory

    def execute(self,
                command: Command,
                std_files: StdFiles,
                process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
        executable = self._executable_factory.make(command)
        try:
            exit_code = subprocess.call(executable.arg_list_or_str,
                                        timeout=process_execution_settings.timeout_in_seconds,
                                        env=process_execution_settings.environ,
                                        shell=executable.is_shell,
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
        msg = 'Error executing {atc} in sub process.'.format(atc=concepts.ACTION_TO_CHECK_CONCEPT_INFO.singular_name)
        return new_eh_hard_error(FailureDetails.new_exception(ex, message=msg))


class _AtcSubProcessExecutorForUnsupportedOperatingSystem(AtcOsProcessExecutor):
    def execute(self,
                command: Command,
                std_files: StdFiles,
                process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
        raise ValueError('System not supported: ' + os.name)


def _atc_os_process_executor_for_current_system() -> AtcOsProcessExecutor:
    try:
        executable_factory = executable_factories.get_factory_for_operating_system(os.name)
        return AtcSubProcessExecutor(executable_factory)
    except KeyError:
        return _AtcSubProcessExecutorForUnsupportedOperatingSystem()


DEFAULT_ATC_OS_PROCESS_EXECUTOR = _atc_os_process_executor_for_current_system()


def _raise_fail_to_make_dir_exception(path: pathlib.Path, ex: Exception):
    raise exception_detection.DetectedException(
        FailureDetails.new_message(
            text_docs.single_line(
                strings.FormatMap(
                    'Failed to make directory {path}',
                    {'path': path}
                )),
            ex
        ))
