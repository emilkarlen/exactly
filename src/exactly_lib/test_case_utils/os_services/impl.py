import pathlib
import shutil

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.exception_detection import DetectedException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util.str_ import str_constructor


class OsServicesForAnyOs(OsServices):
    def __init__(self,
                 command_executor: CommandExecutor,
                 ):
        self._command_executor = command_executor

    @property
    def command_executor(self) -> CommandExecutor:
        return self._command_executor

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
                )
            )


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
