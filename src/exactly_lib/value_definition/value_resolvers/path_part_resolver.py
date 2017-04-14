from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.util.symbol_table import SymbolTable


class PathPartResolver:
    """
    The relative path that follows the root path of the `FileRef`.
    """

    def resolve(self, symbols: SymbolTable) -> PathPart:
        raise NotImplementedError()

    @property
    def references(self) -> list:
        """
        :rtype: [ValueReference]
        """
        raise NotImplementedError()
