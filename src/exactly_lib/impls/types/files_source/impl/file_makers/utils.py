from typing import Callable

from exactly_lib.common.report_rendering.parts import failure_details as _fd_rendering
from exactly_lib.impls import file_properties
from exactly_lib.impls.file_properties import FileType, CheckResult
from exactly_lib.impls.types.path import path_err_msgs
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.result import failure_details
from exactly_lib.type_val_prims.described_path import DescribedPath


class NewFileCreator:
    _PATH_CREATION_FAILURE = 'Failed to create path'
    _FILE_EXISTENCE_CHECK = file_properties.must_exist(follow_symlinks=False)
    _PROPERTIES_FOR_ERR_MSG = file_properties.PropertiesWithNegation(
        True,
        file_properties.new_properties_for_existence(follow_symlinks=False,
                                                     file_exists=True),
    )

    def __init__(self, maker: Callable[[DescribedPath], None]):
        self._maker = maker

    def make(self, path: DescribedPath):
        self._assert_is_valid_path(path)
        try:
            self._maker(path)
        except OSError as ex:
            failure = failure_details.FailureDetails(
                path_err_msgs.line_header__primitive__path(
                    self._PATH_CREATION_FAILURE,
                    path),
                ex
            )
            raise HardErrorException(_fd_rendering.FailureDetailsRenderer(failure))

    def _assert_is_valid_path(self, path: DescribedPath):
        result = self._FILE_EXISTENCE_CHECK.apply(path.primitive)
        if result.is_success:
            raise HardErrorException(
                file_properties.render_failure__d(self._PROPERTIES_FOR_ERR_MSG, path)
            )


class ExistingFileModifier:
    def __init__(self,
                 file_type: FileType,
                 maker: Callable[[DescribedPath], None],
                 ):
        self._file_check = file_properties.must_exist_as(file_type, follow_symlinks=True)
        self._maker = maker

    def make(self, path: DescribedPath):
        self._assert_is_valid_path(path)
        self._maker(path)

    def _assert_is_valid_path(self, path: DescribedPath):
        result = self._file_check.apply(path.primitive)
        _raise_hard_error_if_not_success(result, path)


def _raise_hard_error_if_not_success(result: CheckResult, path: DescribedPath):
    if not result.is_success:
        raise HardErrorException(
            file_properties.render_failure__d(result.cause, path)
        )
