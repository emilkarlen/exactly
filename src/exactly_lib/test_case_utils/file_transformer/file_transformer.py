import pathlib

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.symbol_table import SymbolTable


class FileTransformer:
    """ Transforms an existing regular file. """

    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  src_file_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError('abstract method')


class FileTransformerResolver:
    """Resolver of a :class:`FileTransformer`"""

    def resolve(self, named_elements: SymbolTable) -> FileTransformer:
        raise NotImplementedError('abstract method')
