from typing import Sequence, Callable, TypeVar

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.test_case_utils.expression.grammar import OperatorExpressionDescription
from exactly_lib.util.textformat.structure.core import ParagraphItem

T = TypeVar('T')


def _mk_empty_sequence() -> Sequence[T]:
    return ()


class OperatorExpressionDescriptionFromFunctions(OperatorExpressionDescription):
    def __init__(self,
                 description_rest: Callable[[], Sequence[ParagraphItem]],
                 see_also_targets: Callable[[], Sequence[SeeAlsoTarget]] = _mk_empty_sequence):
        self._description_rest = description_rest
        self._see_also_targets = see_also_targets

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return self._description_rest()

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return self._see_also_targets()
