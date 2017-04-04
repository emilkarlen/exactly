from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.value_definition.value_structure import Value


class StringValue(Value):
    def __init__(self, string: str):
        self._string = string

    @property
    def string(self) -> str:
        return self._string

    @property
    def references(self) -> list:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + self._string + '\''


class FileRefValue(Value):
    def __init__(self, file_ref: FileRef):
        self._file_ref = file_ref

    @property
    def file_ref(self) -> FileRef:
        return self._file_ref

    @property
    def references(self) -> list:
        return self._file_ref.value_references()

    def __str__(self):
        return str(type(self)) + '\'' + str(self._file_ref) + '\''


class ValueVisitor:
    """
    Visitor of `Value`
    """

    def visit(self, value: Value):
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, FileRefValue):
            return self._visit_file_ref(value)
        if isinstance(value, StringValue):
            return self._visit_string(value)
        raise TypeError('Unknown {}: {}'.format(Value, str(value)))

    def _visit_string(self, value: StringValue):
        raise NotImplementedError()

    def _visit_file_ref(self, value: FileRefValue):
        raise NotImplementedError()
