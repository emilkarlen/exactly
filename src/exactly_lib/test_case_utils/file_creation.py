import pathlib
from typing import Optional, Any, Callable, TextIO

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.parts import failure_details as failure_details_rendering
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.exception_detection import DetectedException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case_utils.err_msg import path_err_msgs
from exactly_lib.test_case_utils.string_models.file_model import StringModelOfFile
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.ensure_file_existence import ensure_directory_exists, \
    ensure_parent_directory_does_exist_and_is_a_directory


def create_file(file_path: pathlib.Path,
                operation_on_open_file: Callable[[TextIO], None]) -> Optional[str]:
    """
    :return: None iff success. Otherwise an error message.
    """
    try:
        if file_path.exists():
            return 'File does already exist: {}'.format(file_path)
    except NotADirectoryError:
        return 'Part of path exists, but perhaps one in-the-middle-component is not a directory: %s' % str(file_path)
    failure_message = ensure_parent_directory_does_exist_and_is_a_directory(file_path)
    if failure_message is not None:
        return failure_message
    try:
        with file_path.open('x') as f:
            operation_on_open_file(f)
    except IOError:
        return 'Cannot create file: {}'.format(file_path)
    return None


def create_file__dp(path: DescribedPath,
                    operation_on_open_file: Callable[[Any], None]) -> Optional[TextRenderer]:
    """
    :return: None iff success. Otherwise an error message.
    """

    def error(header: str) -> TextRenderer:
        return path_err_msgs.line_header__primitive(
            header,
            path.describer,
        )

    file_path = path.primitive
    try:
        if file_path.exists():
            return error('File already exists')
    except NotADirectoryError:
        return error('Part of path exists, but perhaps one in-the-middle-component is not a directory')
    failure_message = ensure_parent_path_does_exist_and_is_a_directory__dp(path)
    if failure_message is not None:
        return failure_message
    try:
        with file_path.open('x') as f:
            operation_on_open_file(f)
    except IOError:
        return error('Cannot create file')
    return None


class FileTransformerHelper:
    def __init__(self,
                 os_services: OsServices,
                 tmp_file_space: DirFileSpace,
                 ):
        self._os_services = os_services
        self._tmp_file_space = tmp_file_space

    def transform_to_file__dp(self,
                              src_path: pathlib.Path,
                              dst_path: DescribedPath,
                              transformer: StringTransformer,
                              ) -> Optional[TextRenderer]:
        error_message = create_file__dp(dst_path, _do_nothing_with_file)
        if error_message is not None:
            return error_message
        return self._transform(src_path,
                               dst_path.primitive,
                               transformer)

    def transform_to_file(self,
                          src_path: pathlib.Path,
                          dst_path: pathlib.Path,
                          transformer: StringTransformer,
                          ) -> Optional[TextRenderer]:
        error_message = create_file(dst_path, _do_nothing_with_file)
        if error_message is not None:
            return text_docs.single_pre_formatted_line_object(error_message)
        return self._transform(src_path,
                               dst_path,
                               transformer)

    def _transform(self,
                   src_path: pathlib.Path,
                   dst_path: pathlib.Path,
                   transformer: StringTransformer,
                   ) -> Optional[TextRenderer]:
        input_model = self._model_of(src_path)
        try:
            output_model = transformer.transform(input_model)
            self._os_services.copy_file__detect_ex(
                output_model.as_file,
                dst_path,
            )
            return None
        except DetectedException as ex:
            return failure_details_rendering.FailureDetailsRenderer(ex.failure_details)
        except HardErrorException as ex:
            return ex.error

    def _model_of(self, file: pathlib.Path) -> StringModel:
        return StringModelOfFile(
            file,
            self._tmp_file_space.sub_dir_space(),
        )


def ensure_path_exists_as_a_directory__dp(path: DescribedPath) -> Optional[TextRenderer]:
    """
    :return: Failure message if cannot ensure, otherwise None.
    """

    def error(header: str) -> TextRenderer:
        return path_err_msgs.line_header__primitive(
            header,
            path.describer,
        )

    try:
        return ensure_directory_exists(path.primitive)
    except NotADirectoryError:
        return error('Not a directory')
    except FileExistsError:
        return error('Part of path exists, but perhaps one in-the-middle-component is not a directory')


def ensure_parent_path_does_exist_and_is_a_directory__dp(dst_path: DescribedPath
                                                         ) -> Optional[TextRenderer]:
    """
    :return: Failure message if cannot ensure, otherwise None.
    """
    return ensure_path_exists_as_a_directory__dp(dst_path.parent())


def _do_nothing_with_file(f: TextIO):
    return
