import pathlib

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.file_transformer import file_transformer as aft
from exactly_lib.util.symbol_table import SymbolTable


class ConstantFileTransformerResolver(aft.FileTransformerResolver):
    def __init__(self, constant: aft.FileTransformer):
        self.constant = constant

    def resolve(self, named_elements: SymbolTable) -> aft.FileTransformer:
        return self.constant


class IdentityFileTransformer(aft.FileTransformer):
    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  actual_file_path: pathlib.Path) -> pathlib.Path:
        return actual_file_path
