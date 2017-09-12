import pathlib

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.util.symbol_table import SymbolTable


class FileTransformer:
    """ Transforms an existing regular file. """

    # TODO: Maybe this class should be removed,
    # it is a wrapping of new LinesTransformer into old structures.
    # But perhaps it is motivated to have it. Have not looked into it.

    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  src_file_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError('abstract method')

    @property
    def corresponding_lines_transformer(self) -> LinesTransformer:
        raise NotImplementedError('abstract method')


class FileTransformerResolver:
    """Resolver of a :class:`FileTransformer`"""

    # TODO: Maybe this class should be removed,
    # it is a wrapping of new LinesTransformer into old structures.
    # But perhaps it is motivated to have it. Have not looked into it.

    @property
    def references(self) -> list:
        """
        :rtype [`NamedElementReference`]:
        """
        return []

    def resolve(self, named_elements: SymbolTable) -> FileTransformer:
        raise NotImplementedError('abstract method')
