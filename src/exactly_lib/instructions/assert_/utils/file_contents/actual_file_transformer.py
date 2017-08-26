import pathlib

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.symbol_table import SymbolTable


class ActualFileTransformer:
    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  actual_file_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError('abstract method')


class PathResolverForEnvVarReplacement:
    def dst_file_path(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      src_file_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError('abstract method')


class ActualFileTransformerResolver:
    def resolve(self, named_elements: SymbolTable) -> ActualFileTransformer:
        raise NotImplementedError('abstract method')
