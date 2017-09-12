import pathlib

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformer, FileTransformerResolver
from exactly_lib.test_case_utils.lines_transformer.transformers import IdentityLinesTransformer
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.util.symbol_table import SymbolTable


class ConstantFileTransformerResolver(FileTransformerResolver):
    def __init__(self, constant: FileTransformer):
        self.constant = constant

    def resolve(self, named_elements: SymbolTable) -> FileTransformer:
        return self.constant


class IdentityFileTransformer(FileTransformer):
    @property
    def corresponding_lines_transformer(self) -> LinesTransformer:
        return IdentityLinesTransformer()

    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  src_file_path: pathlib.Path) -> pathlib.Path:
        return src_file_path
