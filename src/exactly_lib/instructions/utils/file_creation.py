import pathlib

from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist_and_is_a_directory


def create_file(file_path: pathlib.Path,
                operation_on_open_file) -> str:
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


def resolve_and_create_file(path_resolver: FileRefResolver,
                            environment: PathResolvingEnvironmentPreOrPostSds,
                            operation_on_open_file) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    return create_file(path_resolver.resolve(environment.symbols).value_post_sds(environment.sds),
                       operation_on_open_file)


def create_file_from_transformation_of_existing_file(src_path: pathlib.Path,
                                                     dst_path: pathlib.Path,
                                                     transformer: LinesTransformer,
                                                     tcds: HomeAndSds) -> str:
    """
    :return: Error message in case of failure
    """

    def write_file(output_file):
        with src_path.open() as in_file:
            for line in transformer.transform(tcds, in_file):
                output_file.write(line)

    return create_file(dst_path,
                       write_file)
