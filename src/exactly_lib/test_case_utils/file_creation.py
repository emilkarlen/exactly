import pathlib
from typing import Optional, Any, Callable

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_utils.err_msg import path_err_msgs
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist_and_is_a_directory, \
    ensure_directory_exists


def create_file(file_path: pathlib.Path,
                operation_on_open_file: Callable[[Any], None]) -> Optional[str]:
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


def create_file_from_transformation_of_existing_file(src_path: pathlib.Path,
                                                     dst_path: pathlib.Path,
                                                     transformer: StringTransformer) -> Optional[str]:
    """
    :return: Error message in case of failure
    """

    def write_file(output_file):
        with src_path.open() as in_file:
            for line in transformer.transform(in_file):
                output_file.write(line)

    return create_file(dst_path,
                       write_file)


def create_file_from_transformation_of_existing_file__dp(src_path: pathlib.Path,
                                                         dst_path: DescribedPath,
                                                         transformer: StringTransformer) -> Optional[TextRenderer]:
    """
    :return: Error message in case of failure
    """

    def write_file(output_file):
        with src_path.open() as in_file:
            for line in transformer.transform(in_file):
                output_file.write(line)

    return create_file__dp(dst_path,
                           write_file)


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
