import pathlib

from exactly_lib.execution import environment_variables
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist


class ActualFileTransformer:
    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  actual_file_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()


class IdentityFileTransformer(ActualFileTransformer):
    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  actual_file_path: pathlib.Path) -> pathlib.Path:
        return actual_file_path


class ActualFileTransformerForEnvVarsReplacementBase(ActualFileTransformer):
    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  actual_file_path: pathlib.Path) -> pathlib.Path:
        src_file_path = actual_file_path
        dst_file_path = self._dst_file_path(environment, src_file_path)
        if dst_file_path.exists():
            return dst_file_path
        env_vars_to_replace = environment_variables.replaced(environment.hds,
                                                             environment.sds)
        self._replace_env_vars_and_write_result_to_dst(env_vars_to_replace,
                                                       src_file_path,
                                                       dst_file_path)
        return dst_file_path

    def _dst_file_path(self,
                       environment: InstructionEnvironmentForPostSdsStep,
                       src_file_path: pathlib.Path) -> pathlib.Path:
        """
        :return: An absolute path that does/should store the transformed version of
        the src file.
        """
        raise NotImplementedError()

    @staticmethod
    def _replace_env_vars_and_write_result_to_dst(env_vars_to_replace: dict,
                                                  src_file_path: pathlib.Path,
                                                  dst_file_path: pathlib.Path):
        with src_file_path.open() as src_file:
            # TODO Handle reading/replacing in chunks, if file is too large to be read in one chunk
            contents = src_file.read()
        for var_name, var_value in env_vars_to_replace.items():
            contents = contents.replace(var_value, var_name)
        ensure_parent_directory_does_exist(dst_file_path)
        with open(str(dst_file_path), 'w') as dst_file:
            dst_file.write(contents)
