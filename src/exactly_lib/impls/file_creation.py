import pathlib
from typing import Optional, Callable, TextIO, TypeVar

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.types.path import path_err_msgs
from exactly_lib.impls.types.string_source import file_source
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.type_val_deps.types.path.path_ddv import DescribedPath
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.ensure_file_existence import ensure_directory_exists, \
    ensure_parent_directory_does_exist_and_is_a_directory


def create_file(file_path: pathlib.Path,
                operation_on_open_file: Callable[[TextIO], None]) -> Optional[str]:
    """
    :return: None iff success. Otherwise an error message.
    """

    def render_error(message: str) -> str:
        return message

    def ensure_parent_path_is_existing_dir() -> Optional[str]:
        return ensure_parent_directory_does_exist_and_is_a_directory(file_path)

    return _create_file(file_path, ensure_parent_path_is_existing_dir, render_error, operation_on_open_file)


def create_file__dp(path: DescribedPath,
                    operation_on_open_file: Callable[[TextIO], None],
                    ) -> Optional[TextRenderer]:
    """
    :return: None iff success. Otherwise an error message.
    """

    def render_error(header: str) -> TextRenderer:
        return path_err_msgs.line_header__primitive(
            header,
            path.describer,
        )

    def ensure_parent_path_is_existing_dir() -> Optional[TextRenderer]:
        return ensure_parent_path_does_exist_and_is_a_directory__dp(path)

    return _create_file(path.primitive, ensure_parent_path_is_existing_dir, render_error, operation_on_open_file)


ERR = TypeVar('ERR')


def _create_file(file_path: pathlib.Path,
                 ensure_parent_path_is_existing_dir: Callable[[], Optional[ERR]],
                 error_renderer: Callable[[str], ERR],
                 operation_on_open_file: Callable[[TextIO], None],
                 ) -> Optional[ERR]:
    """
    :return: None iff success. Otherwise an error message.
    """
    try:
        file_path.lstat()
        return error_renderer('File already exists')
    except NotADirectoryError:
        return error_renderer('Part of path exists, but perhaps one in-the-middle-component is not a directory')
    except:
        pass

    failure_message = ensure_parent_path_is_existing_dir()
    if failure_message is not None:
        return failure_message

    try:
        f = file_path.open('x')
    except OSError as ex:
        return error_renderer('Cannot create file\n' + str(ex))

    try:
        operation_on_open_file(f)
    except:
        f.close()
        file_path.unlink()
        raise
    else:
        f.close()

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
            self._os_services.copy_file(
                output_model.contents().as_file,
                dst_path,
            )
            return None
        except HardErrorException as ex:
            return ex.error

    def _model_of(self, file: pathlib.Path) -> StringSource:
        return file_source.string_source_of_file__poorly_described(
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
