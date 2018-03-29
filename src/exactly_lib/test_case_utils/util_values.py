from typing import Optional

from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.value_type import DataValueType


class StringOrFileRefValue(tuple):
    """
    Either a :class:`StringValue` or a :class:`FileRef`
    """

    def __new__(cls,
                string_value: Optional[StringValue],
                file_value: Optional[FileRef]):
        return tuple.__new__(cls, (DataValueType.STRING if string_value else DataValueType.PATH,
                                   string_value,
                                   file_value))

    @property
    def value_type(self) -> DataValueType:
        """
        :return: Either STRING or PATH
        """
        return self[0]

    @property
    def is_file_ref(self) -> bool:
        """
        Tells if the source is a path.
        If not, it is a string accessed via `string_value`
        """
        return self.value_type is DataValueType.PATH

    @property
    def string_value(self) -> StringValue:
        """
        :return: Not None iff :class:`DataValueType` is NOT `DataValueType.STRING`
        """
        return self[1]

    @property
    def file_ref_value(self) -> FileRef:
        """
        :return: Not None iff :class:`DataValueType` is `DataValueType.PATH`
        """
        return self[2]


def of_string(string_value: StringValue) -> StringOrFileRefValue:
    return StringOrFileRefValue(string_value, None)


def of_file_ref(file_ref: FileRef) -> StringOrFileRefValue:
    return StringOrFileRefValue(None, file_ref)
