import os
import pathlib
import shutil

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.test_case import exception_detection, executable_factories
from exactly_lib.test_case.executable_factory import ExecutableFactory
from exactly_lib.test_case.result import sh
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util.str_ import str_constructor


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

    def copy_file__detect_ex(self, src: pathlib.Path, dst: pathlib.Path):
        """
        :param src: A readable regular file.
        :param dst: Will be overwritten if it exists.
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
            raise exception_detection.DetectedException(
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
            raise exception_detection.DetectedException(
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

    def executable_factory__detect_ex(self) -> ExecutableFactory:
        if self._platform_system_not_supported:
            raise exception_detection.DetectedException(
                FailureDetails.new_constant_message(self._platform_system_not_supported)
            )
        return self._executable_factory


def _raise_fail_to_make_dir_exception(path: pathlib.Path, ex: Exception):
    raise exception_detection.DetectedException(
        FailureDetails.new_message(
            text_docs.single_line(
                str_constructor.FormatMap(
                    'Failed to make directory {path}',
                    {'path': path}
                )),
            ex
        ))
