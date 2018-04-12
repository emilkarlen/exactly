from typing import Sequence, Set, Callable

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic import lines_transformer
from exactly_lib.type_system.logic.lines_transformer import LinesTransformerValue, LinesTransformer
from exactly_lib.type_system.utils import resolving_dependencies_from_sequence


class LinesTransformerConstantValue(LinesTransformerValue):
    """
    A :class:`LinesTransformerResolver` that is a constant :class:`LinesTransformer`
    """

    def __init__(self, value: LinesTransformer):
        self._value = value

    def value_when_no_dir_dependencies(self) -> LinesTransformer:
        return self._value

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> LinesTransformer:
        return self._value


class LinesTransformerSequenceValue(LinesTransformerValue):
    def __init__(self, sequence: Sequence[LinesTransformerValue]):
        self._sequence = sequence

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return resolving_dependencies_from_sequence(self._sequence)

    def value_when_no_dir_dependencies(self) -> LinesTransformer:
        return lines_transformer.SequenceLinesTransformer([
            transformer.value_when_no_dir_dependencies()
            for transformer in self._sequence
        ])

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> lines_transformer.SequenceLinesTransformer:
        return lines_transformer.SequenceLinesTransformer([
            transformer.value_of_any_dependency(home_and_sds)
            for transformer in self._sequence
        ])


class DirDependentLinesTransformerValue(LinesTransformerValue):
    def __init__(self,
                 dependencies: Set[DirectoryStructurePartition],
                 constructor: Callable[[HomeAndSds], LinesTransformer]):
        self._constructor = constructor
        self._dependencies = dependencies

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._dependencies

    def exists_pre_sds(self) -> bool:
        return DirectoryStructurePartition.NON_HOME not in self.resolving_dependencies()

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> LinesTransformer:
        return self._constructor(home_and_sds)
