import pathlib

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.file_transformer import file_transformer as aft, env_vars_replacement
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist


class PathResolverForEnvVarReplacement:
    def dst_file_path(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      src_file_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError('abstract method')


class FileTransformerForEnvVarsReplacement(aft.FileTransformer):
    def __init__(self,
                 dst_path_resolver: PathResolverForEnvVarReplacement):
        self._dst_path_resolver = dst_path_resolver

    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  actual_file_path: pathlib.Path) -> pathlib.Path:
        src_file_path = actual_file_path
        dst_file_path = self._dst_path_resolver.dst_file_path(environment, src_file_path)
        if dst_file_path.exists():
            return dst_file_path
        self._replace_env_vars_and_write_result_to_dst(environment.home_and_sds,
                                                       src_file_path,
                                                       dst_file_path)
        return dst_file_path

    @staticmethod
    def _replace_env_vars_and_write_result_to_dst(home_and_sds: HomeAndSds,
                                                  src_file_path: pathlib.Path,
                                                  dst_file_path: pathlib.Path):
        with src_file_path.open() as src_file:
            original_contents = src_file.read()
        replaced_contents = env_vars_replacement.replace(home_and_sds, original_contents)
        ensure_parent_directory_does_exist(dst_file_path)
        with open(str(dst_file_path), 'w') as dst_file:
            dst_file.write(replaced_contents)
