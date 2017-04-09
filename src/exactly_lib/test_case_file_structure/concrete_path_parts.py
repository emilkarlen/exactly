from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.concrete_restrictions import StringRestriction
from exactly_lib.value_definition.concrete_values import StringValue
from exactly_lib.value_definition.value_structure import ValueReference, ValueContainer


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


class PathPartAsStringSymbolReference(PathPart):
    def __init__(self, symbol_name: str):
        self._value_reference = ValueReference(symbol_name, StringRestriction())

    def resolve(self, symbols: SymbolTable) -> str:
        value_container = symbols.lookup(self.symbol_name)
        assert isinstance(value_container, ValueContainer)
        string_value = value_container.value
        assert isinstance(string_value, StringValue)
        return string_value.resolve(symbols)

    @property
    def value_references(self) -> list:
        return [self._value_reference]

    @property
    def symbol_name(self) -> str:
        return self._value_reference.name


class PathPartVisitor:
    def visit(self, path_suffix: PathPart):
        if isinstance(path_suffix, PathPartAsFixedPath):
            return self.visit_fixed_path(path_suffix)
        elif isinstance(path_suffix, PathPartAsStringSymbolReference):
            return self.visit_symbol_reference(path_suffix)
        raise TypeError('Not a {}: {}'.format(str(PathPart), path_suffix))

    def visit_fixed_path(self, path_suffix: PathPartAsFixedPath):
        raise NotImplementedError()

    def visit_symbol_reference(self, path_suffix: PathPartAsStringSymbolReference):
        raise NotImplementedError()
