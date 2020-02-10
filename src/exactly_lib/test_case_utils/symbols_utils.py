from typing import Iterable, Set

from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.lookups import lookup_container
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.util.symbol_table import SymbolTable


def resolving_dependencies_from_references(references: Iterable[SymbolReference],
                                           symbols: SymbolTable) -> Set[DirectoryStructurePartition]:
    ret_val = set()
    for reference in references:
        sdv = lookup_container(symbols, reference.name).sdv
        if isinstance(sdv, PathSdv):
            resolving_dependency = sdv.resolve(symbols).resolving_dependency()
            if resolving_dependency is not None:
                ret_val.add(resolving_dependency)
        else:
            ret_val.update(resolving_dependencies_from_references(sdv.references,
                                                                  symbols))
    return ret_val
