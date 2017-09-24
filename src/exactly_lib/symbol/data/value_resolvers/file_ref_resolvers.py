from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.test_case_file_structure import relativity_root
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsNothing
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.path_part import PathPart
from exactly_lib.util.symbol_table import SymbolTable


def resolver_of_rel_option(rel_option: relativity_root.RelOptionType,
                           path_suffix: PathPart = PathPartAsNothing()) -> FileRefResolver:
    return FileRefConstant(file_refs.of_rel_option(rel_option, path_suffix))


class FileRefConstant(FileRefResolver):
    """
    A `FileRefResolver` that is a constant `FileRef`
    """

    def __init__(self, file_ref: FileRef):
        self._file_ref = file_ref

    def resolve(self, symbols: SymbolTable) -> FileRef:
        return self._file_ref

    @property
    def references(self) -> list:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._file_ref) + '\''
