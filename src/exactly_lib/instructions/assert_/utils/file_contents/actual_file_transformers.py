import pathlib

from exactly_lib.instructions.assert_.utils.file_contents import env_vars_replacement
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist
from exactly_lib.util.symbol_table import SymbolTable


class ActualFileTransformer:
    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  actual_file_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()


class PathResolverForEnvVarReplacement:
    def dst_file_path(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      src_file_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError('abstract method')


class ActualFileTransformerResolver:
    def resolve(self, named_elements: SymbolTable) -> ActualFileTransformer:
        raise NotImplementedError('abstract method')


class ConstantActualFileTransformerResolver(ActualFileTransformerResolver):
    def __init__(self, constant: ActualFileTransformer):
        self.constant = constant

    def resolve(self, named_elements: SymbolTable) -> ActualFileTransformer:
        return self.constant


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
        dst_file_path = self.get_path_resolver().dst_file_path(environment, src_file_path)
        if dst_file_path.exists():
            return dst_file_path
        self._replace_env_vars_and_write_result_to_dst(environment.home_and_sds,
                                                       src_file_path,
                                                       dst_file_path)
        return dst_file_path

    def get_path_resolver(self) -> PathResolverForEnvVarReplacement:
        raise NotImplementedError('abstract method')

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
