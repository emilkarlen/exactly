from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.util.symbol_table import SymbolTable


class PathPartAsFixedPath(PathPart):
    def __init__(self, file_name: str):
        self._file_name = file_name

    @property
    def file_name(self) -> str:
        return self._file_name

    def resolve(self, symbols: SymbolTable) -> str:
        return self._file_name

    @property
    def value_references(self) -> list:
        return []


class PathPartAsNothing(PathPart):
    def resolve(self, symbols: SymbolTable) -> str:
        return ''

    @property
    def value_references(self) -> list:
        return []


class PathPartVisitor:
    def visit(self, path_suffix: PathPart):
        if isinstance(path_suffix, PathPartAsFixedPath):
            return self.visit_fixed_path(path_suffix)
        elif isinstance(path_suffix, PathPartAsNothing):
            return self.visit_nothing(path_suffix)
        raise TypeError('Not a {}: {}'.format(str(PathPart), path_suffix))

    def visit_fixed_path(self, path_suffix: PathPartAsFixedPath):
        raise NotImplementedError()

    def visit_nothing(self, path_suffix: PathPartAsNothing):
        raise NotImplementedError()
