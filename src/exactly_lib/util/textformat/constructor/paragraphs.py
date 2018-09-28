from typing import List, Iterable

from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.paragraph import ParagraphItemsConstructor
from exactly_lib.util.textformat.structure.core import ParagraphItem


def constant(paragraphs: Iterable[ParagraphItem]) -> ParagraphItemsConstructor:
    return _Constant(paragraphs)


def sequence(constructors: Iterable[ParagraphItemsConstructor]) -> ParagraphItemsConstructor:
    return _Sequence(constructors)


def empty() -> ParagraphItemsConstructor:
    return _Constant([])


class _Constant(ParagraphItemsConstructor):
    def __init__(self, paragraph_items: Iterable[ParagraphItem]):
        self._paragraph_items = paragraph_items

    def apply(self, environment: ConstructionEnvironment) -> List[ParagraphItem]:
        return list(self._paragraph_items)


class _Sequence(ParagraphItemsConstructor):
    def __init__(self, constructors: Iterable[ParagraphItemsConstructor]):
        self._constructors = constructors

    def apply(self, environment: ConstructionEnvironment) -> List[ParagraphItem]:
        ret_val = []
        for constructor in self._constructors:
            ret_val += constructor.apply(environment)
        return ret_val
