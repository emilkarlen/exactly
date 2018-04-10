from typing import List, Sequence

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget, CrossReferenceId
from exactly_lib.util.collection import FrozenSetBasedOnEquality
from exactly_lib.util.textformat.structure.core import Text, CrossReferenceText, UrlCrossReferenceTarget, StringText


class SeeAlsoItem:
    pass


class CrossReferenceIdSeeAlsoItem(SeeAlsoItem):
    def __init__(self, cross_ref: CrossReferenceId):
        self._cross_ref = cross_ref

    @property
    def cross_reference_id(self) -> CrossReferenceId:
        return self._cross_ref


class TextSeeAlsoItem(SeeAlsoItem):
    def __init__(self, text: Text):
        self._text = text

    @property
    def text(self) -> Text:
        return self._text


class SeeAlsoUrlInfo(tuple, SeeAlsoTarget):
    def __new__(cls,
                title: str,
                url: str):
        return tuple.__new__(cls, (title, url))

    @property
    def title(self) -> str:
        return self[0]

    @property
    def url(self) -> str:
        return self[1]


def see_also_url(url_info: SeeAlsoUrlInfo) -> SeeAlsoItem:
    return TextSeeAlsoItem(
        CrossReferenceText(StringText(url_info.title),
                           UrlCrossReferenceTarget(url_info.url),
                           target_is_id_in_same_document=False,
                           allow_rendering_of_visible_extra_target_text=True))


def see_also_items_from_cross_refs(cross_refs: list) -> list:
    return [CrossReferenceIdSeeAlsoItem(x) for x in cross_refs]


class SeeAlsoItemVisitor:
    def visit(self, x: SeeAlsoItem):
        """
        :return: Return value from _visit... method
        """
        if isinstance(x, CrossReferenceIdSeeAlsoItem):
            return self.visit_cross_reference_id(x)
        elif isinstance(x, TextSeeAlsoItem):
            return self.visit_text(x)
        else:
            raise TypeError('Unknown {}: {}'.format(SeeAlsoItem, str(x)))

    def visit_cross_reference_id(self, x: CrossReferenceIdSeeAlsoItem):
        raise NotImplementedError()

    def visit_text(self, x: TextSeeAlsoItem):
        raise NotImplementedError()


class SeeAlsoSet(tuple):
    """
    Set of :class:`SeeAlsoTarget`
    """

    def __new__(cls,
                cross_reference_or_see_also_url_info_list: Sequence[SeeAlsoTarget]):
        return tuple.__new__(cls, (FrozenSetBasedOnEquality(cross_reference_or_see_also_url_info_list),))

    def union(self, see_also_set):
        return SeeAlsoSet(list(self[0].union(see_also_set[0]).elements))

    @property
    def see_also_items(self) -> List[SeeAlsoItem]:
        return [self._see_also_item(x)
                for x in self[0].elements
                ]

    @staticmethod
    def _see_also_item(x) -> SeeAlsoItem:
        if isinstance(x, CrossReferenceId):
            return CrossReferenceIdSeeAlsoItem(x)
        elif isinstance(x, SeeAlsoUrlInfo):
            return see_also_url(x)
        else:
            raise TypeError('Expected: {} or {}: Found{}'.format(CrossReferenceId, SeeAlsoUrlInfo, x))


def no_see_also() -> SeeAlsoSet:
    return SeeAlsoSet([])
