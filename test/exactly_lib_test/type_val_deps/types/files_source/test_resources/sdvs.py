from abc import ABC

from exactly_lib.type_val_deps.types.files_source.ddv import FilesSourceDdv
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.type_val_deps.types.files_source.test_resources.ddvs import \
    FilesSourceDdvConstantPrimitiveTestImpl


class FilesSourceSdvTestImpl(FilesSourceSdv, ABC):
    pass


class FilesSourceSdvConstantPrimitiveTestImpl(FilesSourceSdvTestImpl):
    def __init__(self, files: FilesSource):
        self._files = files

    def resolve(self, symbols: SymbolTable) -> FilesSourceDdv:
        return FilesSourceDdvConstantPrimitiveTestImpl(self._files)


class FilesSourceSdvConstantDdvTestImpl(FilesSourceSdvTestImpl):
    def __init__(self, constant: FilesSourceDdv):
        self._constant = constant

    def resolve(self, symbols: SymbolTable) -> FilesSourceDdv:
        return self._constant
