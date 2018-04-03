import enum
from typing import Sequence

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.symbol.utils import DirDepValueResolver
from exactly_lib.type_system.logic.program.string_or_file_ref_values import StringOrFileRefValue
from exactly_lib.util.symbol_table import SymbolTable


class SourceType(enum.Enum):
    STRING = 1
    HERE_DOC = 2
    PATH = 3


class StringOrFileRefResolver(DirDepValueResolver[StringOrFileRefValue]):
    def __init__(self,
                 source_type: SourceType,
                 string_resolver: StringResolver,
                 file_reference: FileRefResolver):
        self._source_type = source_type
        self._string = string_resolver
        self._file_ref = file_reference
        self._references = (string_resolver.references
                            if string_resolver is not None
                            else file_reference.references)

    @property
    def source_type(self) -> SourceType:
        return self._source_type

    @property
    def is_file_ref(self) -> bool:
        """
        Tells if the source is a path.
        If not, it is either a string or a here doc accessed via `string_resolver`
        """
        return self.source_type is SourceType.PATH

    @property
    def string_resolver(self) -> StringResolver:
        """
        :return: Not None iff :class:`SourceType` is NOT `SourceType.PATH`
        """
        return self._string

    @property
    def file_reference_resolver(self) -> FileRefResolver:
        """
        :return: Not None iff :class:`SourceType` is `SourceType.PATH`
        """
        return self._file_ref

    def resolve_value(self, symbols: SymbolTable) -> StringOrFileRefValue:
        if self.is_file_ref:
            return StringOrFileRefValue(None, self._file_ref.resolve(symbols))
        else:
            return StringOrFileRefValue(self._string.resolve(symbols), None)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.symbol_usages

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return self._references
