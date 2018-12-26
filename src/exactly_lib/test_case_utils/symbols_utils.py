from typing import Iterable, Set

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.lookups import lookup_container
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.util.symbol_table import SymbolTable


def resolving_dependencies_from_references(references: Iterable[SymbolReference],
                                           symbols: SymbolTable) -> Set[DirectoryStructurePartition]:
    ret_val = set()
    for reference in references:
        resolver = lookup_container(symbols, reference.name).resolver
        if isinstance(resolver, FileRefResolver):
            resolving_dependency = resolver.resolve(symbols).resolving_dependency()
            if resolving_dependency is not None:
                ret_val.add(resolving_dependency)
        else:
            ret_val.update(resolving_dependencies_from_references(resolver.references,
                                                                  symbols))
    return ret_val
