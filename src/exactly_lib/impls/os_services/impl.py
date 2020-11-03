import pathlib
import shutil
from typing import Mapping

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.parts import failure_details
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.str_.str_constructor import ToStringObject


class OsServicesForAnyOs(OsServices):
    def __init__(self,
                 command_executor: CommandExecutor,
                 ):
        self._command_executor = command_executor

    @property
    def command_executor(self) -> CommandExecutor:
        return self._command_executor

    def make_dir_if_not_exists(self, path: pathlib.Path):
        try:
            path.mkdir(parents=True, exist_ok=True)
        except FileExistsError as ex:
            _raise_he__fail_to_make_dir(path, ex)
        except OSError as ex:
            _raise_he__fail_to_make_dir(path, ex)

    def copy_file__preserve_as_much_as_possible(self, src: str, dst: str):
        try:
            shutil.copy2(src, dst)
        except OSError as ex:
            _raise_he__single_line(
                'Failed to copy file {src} -> {dst}',
                {'src': src,
                 'dst': dst},
                ex,
            )

    def copy_file(self, src: pathlib.Path, dst: pathlib.Path):
        try:
            with src.open('r') as src_f:
                with dst.open('w') as dst_f:
                    shutil.copyfileobj(src_f, dst_f)
        except IOError as ex:
            _raise_he__single_line(
                'Failed to copy file {src} -> {dst}',
                {'src': src,
                 'dst': dst},
                ex,
            )
        except Exception as ex:
            raise ValueError('Failed to copy file {} -> {}'.format(src, dst))

    def copy_tree__preserve_as_much_as_possible(self, src: str, dst: str):
        try:
            shutil.copytree(src, dst)
        except OSError as ex:
            _raise_he__single_line(
                'Failed to copy tree {src} -> {dst}',
                {'src': src,
                 'dst': dst},
                ex,
            )


def _raise_he__fail_to_make_dir(path: pathlib.Path, ex: Exception):
    _raise_he__single_line('Failed to make directory {path}', {'path': path}, ex)


def _raise_he__single_line(format_str: str,
                           format_map: Mapping[str, ToStringObject],
                           ex: Exception,
                           ):
    raise HardErrorException(
        failure_details.FailureDetailsRenderer(
            FailureDetails.new_message(
                text_docs.single_line(
                    str_constructor.FormatMap(
                        format_str,
                        format_map
                    )),
                ex
            )
        )
    )
