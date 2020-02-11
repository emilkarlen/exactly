from typing import Sequence, Optional

from exactly_lib.symbol import sdv_validation
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDependentValue
from exactly_lib.symbol.sdv_validation import SdvValidator
from exactly_lib.test_case_utils.file_properties import FileType, must_exist_as
from exactly_lib.type_system.data.string_or_path_ddvs import StringOrPathDdv, SourceType
from exactly_lib.util.symbol_table import SymbolTable


class StringOrPathSdv(SymbolDependentValue):
    def __init__(self,
                 source_type: SourceType,
                 string: Optional[StringSdv],
                 path: Optional[PathSdv]):
        self._source_type = source_type
        self._string = string
        self._path = path
        self._references = (string.references
                            if string is not None
                            else path.references)

    @property
    def source_type(self) -> SourceType:
        return self._source_type

    @property
    def is_path(self) -> bool:
        """
        Tells if the source is a path.
        If not, it is either a string or a here doc accessed via `string_sdv`
        """
        return self.source_type is SourceType.PATH

    @property
    def string_sdv(self) -> StringSdv:
        """
        :return: Not None iff :class:`SourceType` is NOT `SourceType.PATH`
        """
        return self._string

    @property
    def path_sdv(self) -> PathSdv:
        """
        :return: Not None iff :class:`SourceType` is `SourceType.PATH`
        """
        return self._path

    def resolve(self, symbols: SymbolTable) -> StringOrPathDdv:
        if self.is_path:
            return StringOrPathDdv(self._source_type,
                                   None,
                                   self._path.resolve(symbols))
        else:
            return StringOrPathDdv(self._source_type,
                                   self._string.resolve(symbols),
                                   None)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.symbol_usages

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return self._references

    def validator__file_must_exist_as(self,
                                      file_type: FileType,
                                      follow_symlinks: bool = True
                                      ) -> SdvValidator:
        if not self.is_path:
            return sdv_validation.ConstantSuccessSdvValidator()
        from exactly_lib.test_case_utils.path_check import PathCheck
        from exactly_lib.test_case_utils.path_check import PathCheckValidator
        frc = PathCheck(self.path_sdv,
                        must_exist_as(file_type, follow_symlinks))
        return PathCheckValidator(frc)
