from exactly_lib.symbol.data import list_sdvs
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.path_check import PathCheckDdvValidator, PathCheckDdv
from exactly_lib.util.symbol_table import SymbolTable


def empty() -> ArgumentsSdv:
    return ArgumentsSdv(list_sdvs.empty(),
                        ())


def new_without_validation(arguments: ListSdv) -> ArgumentsSdv:
    return ArgumentsSdv(arguments, ())


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
