from exactly_lib.test_case.file_ref import FileRef
from exactly_lib.test_case.file_ref_relativity import PathRelativityVariants
from exactly_lib.util import symbol_table
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import Value


class FileRefValue(Value):
    def __init__(self, source: Line, file_ref: FileRef):
        self._source = source
        self._file_ref = file_ref

    @property
    def source(self) -> Line:
        return self._source

    @property
    def file_ref(self) -> FileRef:
        return self._file_ref


class ValueUsage(object):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class ValueDefinition(ValueUsage):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def value(self) -> symbol_table.Value:
        raise NotImplementedError()

    @property
    def symbol_table_entry(self) -> symbol_table.Entry:
        return symbol_table.Entry(self.name, self.value)


class ValueReference(ValueUsage):
    pass


class ValueDefinitionOfPath(ValueDefinition):
    def __init__(self, name: str, value: FileRefValue):
        super().__init__(name)
        self._value = value

    @property
    def value(self) -> FileRefValue:
        return self._value

    @property
    def symbol_table_entry(self) -> symbol_table.Entry:
        return symbol_table.Entry(self.name, self.value)


class ValueReferenceOfPath(ValueReference):
    """
    A `ValueReference` to a variable that denotes a path with any
    of a given set of valid relativities.
    """

    def __init__(self, name: str, valid_relativities: PathRelativityVariants):
        super().__init__(name)
        self._valid_variants = valid_relativities

    @property
    def valid_relativities(self) -> PathRelativityVariants:
        return self._valid_variants


class ValueReferenceVisitor:
    """
    Visitor of `ValueReference`
    """
    def visit(self, value_reference: ValueReference):
        """
        :return: Return value from _visit... method
        """
        if isinstance(value_reference, ValueReferenceOfPath):
            return self._visit_path(value_reference)
        raise TypeError('Unknown {}: {}'.format(ValueReference, str(value_reference)))

    def _visit_path(self, path_reference: ValueReferenceOfPath):
        raise NotImplementedError()


class ValueDefinitionVisitor:
    """
    Visitor of `ValueDefinition`
    """

    def visit(self, value_definition: ValueDefinition):
        """
        :return: Return value from _visit... method
        """
        if isinstance(value_definition, ValueDefinitionOfPath):
            return self._visit_path(value_definition)
        raise TypeError('Unknown {}: {}'.format(ValueReference, str(value_definition)))

    def _visit_path(self, value_definition: ValueDefinitionOfPath):
        raise NotImplementedError()
