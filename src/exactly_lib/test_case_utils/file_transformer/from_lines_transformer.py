import pathlib

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformer
from exactly_lib.type_system_values.lines_transformer import LinesTransformer
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist


class DestinationFilePathResolver:
    """
    Resolves a destination path that is somehow related to a given source file path.
    """

    def dst_file_path(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      src_file_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError('abstract method')


class FileTransformerFromLinesTransformer(FileTransformer):
    """
    Produces a new destination file, if it does not already exist.

    If it exists, it is reused.

    NO optimization is performed, by inspecting the :class:`LinesTransformer`
    (e.g. to see if it is the identity transformer).
    (So that kind of optimizations should have been done in another place.)
    """

    def __init__(self,
                 dst_path_resolver: DestinationFilePathResolver,
                 lines_transformer: LinesTransformer):
        self._dst_path_resolver = dst_path_resolver
        self._lines_transformer = lines_transformer

    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  actual_file_path: pathlib.Path) -> pathlib.Path:
        src_file_path = actual_file_path
        dst_file_path = self._dst_path_resolver.dst_file_path(environment, src_file_path)
        if dst_file_path.exists():
            return dst_file_path
        self._produce_new_dst_file(environment.home_and_sds,
                                   src_file_path,
                                   dst_file_path)
        return dst_file_path

    def _produce_new_dst_file(self, home_and_sds: HomeAndSds,
                              src_file_path: pathlib.Path,
                              dst_file_path: pathlib.Path):
        ensure_parent_directory_does_exist(dst_file_path)
        with src_file_path.open() as src_file:
            with dst_file_path.open('w') as dst_file:
                input_lines = (line for line in src_file)
                for output_line in self._lines_transformer.transform(home_and_sds, input_lines):
                    dst_file.write(output_line)
