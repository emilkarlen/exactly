import enum
from typing import Sequence

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.symbol_usage import SymbolReference


class SourceType(enum.Enum):
    STRING = 1
    HERE_DOC = 2
    PATH = 3


class StringOrFileRefResolver(tuple):
    def __new__(cls,
                source_type: SourceType,
                string_resolver: StringResolver,
                file_reference: FileRefResolver):
        return tuple.__new__(cls, (source_type,
                                   string_resolver,
                                   file_reference,
                                   (string_resolver.references
                                    if string_resolver is not None
                                    else file_reference.references)))

    @property
    def source_type(self) -> SourceType:
        return self[0]

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
        return self[1]

    @property
    def file_reference_resolver(self) -> FileRefResolver:
        """
        :return: Not None iff :class:`SourceType` is `SourceType.PATH`
        """
        return self[2]

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return self[3]
