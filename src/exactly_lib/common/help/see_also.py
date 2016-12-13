from exactly_lib.common.help.cross_reference_id import CrossReferenceId
from exactly_lib.util.textformat.structure.core import Text


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
