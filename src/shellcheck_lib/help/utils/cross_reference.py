from shellcheck_lib.help.cross_reference_id import CrossReferenceIdVisitor, ConceptCrossReferenceId, CrossReferenceId
from shellcheck_lib.util.textformat.structure.core import Text, CrossReferenceText


class CrossReferenceTextConstructor(object):
    def apply(self, x: CrossReferenceId) -> Text:
        return CrossReferenceText(_TITLE_RENDERER.visit(x),
                                  x)


class _TitleRenderer(CrossReferenceIdVisitor):
    def visit_concept(self, x: ConceptCrossReferenceId):
        return 'Concept "' + x.concept_name + '"'


_TITLE_RENDERER = _TitleRenderer()
