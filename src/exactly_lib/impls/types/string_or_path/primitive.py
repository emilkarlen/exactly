import enum
from typing import Optional

from exactly_lib.symbol.value_type import DataValueType
from exactly_lib.type_val_prims.described_path import DescribedPath


class SourceType(enum.Enum):
    STRING = 1
    HERE_DOC = 2
    PATH = 3


class StringOrPath(tuple):
    """
    Either a :class:`str` or a :class:`pathlib.Path`
    """

    def __new__(cls,
                source_type: SourceType,
                string_value: Optional[str],
                file_value: Optional[DescribedPath]):
        return tuple.__new__(cls, (DataValueType.STRING if string_value is not None else DataValueType.PATH,
                                   string_value,
                                   file_value,
                                   source_type))

    @property
    def value_type(self) -> DataValueType:
        """
        :return: Either STRING or PATH
        """
        return self[0]

    @property
    def is_path(self) -> bool:
        """
        Tells if the source is a path.
        If not, it is a string accessed via `string_value`
        """
        return self.value_type is DataValueType.PATH

    @property
    def string_value(self) -> str:
        """
        :return: Not None iff :class:`DataValueType` is NOT `DataValueType.STRING`
        """
        return self[1]

    @property
    def path_value(self) -> DescribedPath:
        """
        :return: Not None iff :class:`DataValueType` is `DataValueType.PATH`
        """
        return self[2]

    @property
    def source_type(self) -> SourceType:
        return self[3]
