from typing import Sequence, Set, Callable

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic import string_transformer
from exactly_lib.type_system.logic.string_transformer import StringTransformerValue, StringTransformer
from exactly_lib.type_system.utils import resolving_dependencies_from_sequence


class StringTransformerConstantValue(StringTransformerValue):
    """
    A :class:`LinesTransformerResolver` that is a constant :class:`LinesTransformer`
    """

    def __init__(self, value: StringTransformer):
        self._value = value

    def value_when_no_dir_dependencies(self) -> StringTransformer:
        return self._value

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringTransformer:
        return self._value


class StringTransformerSequenceValue(StringTransformerValue):
    def __init__(self, sequence: Sequence[StringTransformerValue]):
        self._sequence = sequence

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return resolving_dependencies_from_sequence(self._sequence)

    def value_when_no_dir_dependencies(self) -> StringTransformer:
        return string_transformer.SequenceStringTransformer([
            transformer.value_when_no_dir_dependencies()
            for transformer in self._sequence
        ])

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> string_transformer.SequenceStringTransformer:
        return string_transformer.SequenceStringTransformer([
            transformer.value_of_any_dependency(home_and_sds)
            for transformer in self._sequence
        ])


class DirDependentStringTransformerValue(StringTransformerValue):
    def __init__(self,
                 dependencies: Set[DirectoryStructurePartition],
                 constructor: Callable[[HomeAndSds], StringTransformer]):
        self._constructor = constructor
        self._dependencies = dependencies

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._dependencies

    def exists_pre_sds(self) -> bool:
        return DirectoryStructurePartition.NON_HOME not in self.resolving_dependencies()

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringTransformer:
        return self._constructor(home_and_sds)
