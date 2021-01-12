from exactly_lib.impls import file_properties
from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.path.path_check import PathCheckDdvValidator, PathCheckDdv
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.symbol_table import SymbolTable


def ref_to_file_that_must_exist(file_that_must_exist: PathSdv,
                                file_type: FileType = FileType.REGULAR) -> ArgumentsSdv:
    def get_file_validator(symbols: SymbolTable) -> DdvValidator:
        return PathCheckDdvValidator(PathCheckDdv(file_that_must_exist.resolve(symbols),
                                                  file_properties.must_exist_as(file_type)))

    return ArgumentsSdv(list_sdvs.from_string(string_sdvs.from_path_sdv(file_that_must_exist)),
                        (get_file_validator,))


def ref_to_path_that_must_exist(file_that_must_exist: PathSdv) -> ArgumentsSdv:
    def get_file_validator(symbols: SymbolTable) -> DdvValidator:
        return PathCheckDdvValidator(PathCheckDdv(file_that_must_exist.resolve(symbols),
                                                  file_properties.must_exist()))

    return ArgumentsSdv(list_sdvs.from_string(string_sdvs.from_path_sdv(file_that_must_exist)),
                        (get_file_validator,))
