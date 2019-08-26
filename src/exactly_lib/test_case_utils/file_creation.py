import pathlib
from typing import Optional, Any, Callable

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_utils.err_msg2 import path_rendering
from exactly_lib.test_case_utils.err_msg2.described_path import DescribedPathPrimitive
from exactly_lib.test_case_utils.err_msg2.header_rendering import SimpleHeaderMinorBlockRenderer
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist_and_is_a_directory, \
    ensure_parent_path_does_exist_and_is_a_directory__dp


def create_file__td(file_path: pathlib.Path,
                    operation_on_open_file: Callable[[Any], None]) -> Optional[TextRenderer]:
    mb_err_msg = create_file(file_path, operation_on_open_file)
    return (
        None
        if mb_err_msg is None
        else text_docs.single_pre_formatted_line_object(mb_err_msg)
    )


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


def create_file__dp(path: DescribedPathPrimitive,
                    operation_on_open_file: Callable[[Any], None]) -> Optional[TextRenderer]:
    """
    :return: None iff success. Otherwise an error message.
    """

    def error(header: str) -> TextRenderer:
        return path_rendering.HeaderAndPathMajorBlocks(
            SimpleHeaderMinorBlockRenderer(header),
            path_rendering.PathRepresentationsRenderersForValue(path.describer)
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


def resolve_and_create_file(path_resolver: FileRefResolver,
                            environment: PathResolvingEnvironmentPreOrPostSds,
                            operation_on_open_file: Callable[[Any], None]) -> Optional[str]:
    """
    :return: None iff success. Otherwise an error message.
    """
    return create_file(path_resolver.resolve(environment.symbols).value_post_sds(environment.sds),
                       operation_on_open_file)


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


def create_file_from_transformation_of_existing_file__td(src_path: pathlib.Path,
                                                         dst_path: pathlib.Path,
                                                         transformer: StringTransformer) -> Optional[TextRenderer]:
    """
    :return: Error message in case of failure
    """

    def write_file(output_file):
        with src_path.open() as in_file:
            for line in transformer.transform(in_file):
                output_file.write(line)

    return create_file__td(dst_path,
                           write_file)
