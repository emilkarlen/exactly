from exactly_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from exactly_lib.util.textformat.structure import document as doc


class RenderingEnvironment(tuple):
    def __new__(cls, cross_ref_text_constructor: CrossReferenceTextConstructor):
        return tuple.__new__(cls, (cross_ref_text_constructor,))

    @property
    def cross_ref_text_constructor(self) -> CrossReferenceTextConstructor:
        return self[0]


class SectionContentsRenderer:
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        raise NotImplementedError()
