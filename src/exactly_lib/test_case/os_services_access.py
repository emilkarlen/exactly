import os
import pathlib
import shutil

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.test_case import executable_factories
from exactly_lib.test_case.exception_detection import DetectedException
from exactly_lib.test_case.executable_factory import ExecutableFactory
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util.process_execution.process_executor import ProcessExecutor
from exactly_lib.util.str_ import str_constructor


def new_for_current_os() -> OsServices:
    """
    :raises :class:`DetectedException`: The current operating system is not supported
    """
    return new_for_os(os.name)


def new_for_current_os__with_environ() -> OsServices:
    """
    :raises :class:`DetectedException`: The current operating system is not supported
    """
    return new_for_current_os()


def new_for_os(os_name: str) -> OsServices:
    """
    :raises :class:`DetectedException`: The given operating system is not supported
    """
    try:
        executable_factory = executable_factories.get_factory_for_operating_system(os_name)
    except KeyError:
        raise DetectedException(
            FailureDetails.new_message(
                text_docs.single_line(
                    'Unsupported Operating System: {}'.format(os_name)),
            )
        )
    return _Default(executable_factory)


class _Default(OsServices):
    def __init__(self,
                 executable_factory: ExecutableFactory,
                 ):
        self._executable_factory = executable_factory

    def process_executor(self) -> ProcessExecutor:
        return ProcessExecutor()

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
            raise DetectedException(
                FailureDetails.new_message(
                    text_docs.single_line(
                        str_constructor.FormatMap(
                            'Failed to copy file {src} -> {dst}',
                            {'src': src,
                             'dst': dst
                             })
                    ),
                    ex)
            )

    def copy_file__detect_ex(self, src: pathlib.Path, dst: pathlib.Path):
        try:
            with src.open('r') as src_f:
                with dst.open('w') as dst_f:
                    shutil.copyfileobj(src_f, dst_f)
        except IOError as ex:
            raise DetectedException(
                FailureDetails.new_message(
                    text_docs.single_line(
                        str_constructor.FormatMap(
                            'Failed to copy file {src} -> {dst}',
                            {'src': src,
                             'dst': dst
                             })
                    ),
                    ex)
            )
        except Exception as ex:
            raise ValueError('error')

    def copy_tree_preserve_as_much_as_possible__detect_ex(self, src: str, dst: str):
        try:
            shutil.copytree(src, dst)
        except OSError as ex:
            raise DetectedException(
                FailureDetails.new_message(
                    text_docs.single_line(
                        str_constructor.FormatMap(
                            'Failed to copy tree {src} -> {dst}',
                            {'src': src,
                             'dst': dst},
                        )
                    ),
                    ex
                ))

    def executable_factory(self) -> ExecutableFactory:
        return self._executable_factory


def _raise_fail_to_make_dir_exception(path: pathlib.Path, ex: Exception):
    raise DetectedException(
        FailureDetails.new_message(
            text_docs.single_line(
                str_constructor.FormatMap(
                    'Failed to make directory {path}',
                    {'path': path}
                )),
            ex
        )
    )
