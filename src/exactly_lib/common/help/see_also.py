from exactly_lib.help_texts.name_and_cross_ref import CrossReferenceId
from exactly_lib.util.textformat.structure.core import Text, CrossReferenceText, UrlCrossReferenceTarget


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


def see_also_url(title: str, url: str) -> SeeAlsoItem:
    return TextSeeAlsoItem(
        CrossReferenceText(title,
                           UrlCrossReferenceTarget(url),
                           target_is_id_in_same_document=False,
                           allow_rendering_of_visible_extra_target_text=True))


class SeeAlsoUrlInfo(tuple):
    def __new__(cls,
                title: str, url: str):
        return tuple.__new__(cls, (title, url))

    @property
    def title(self) -> str:
        return self[0]

    @property
    def url(self) -> str:
        return self[1]


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


class CrossReferenceIdSet(tuple):
    def __new__(cls,
                cross_references: list):
        return tuple.__new__(cls, (tuple(cross_references),))

    @property
    def cross_references(self) -> tuple:
        return self[0]

    def union(self, other):
        ret_val = list(self.cross_references)
        for o in other.cross_references:
            if not o in self.cross_references:
                ret_val.append(o)
        return CrossReferenceIdSet(ret_val)
