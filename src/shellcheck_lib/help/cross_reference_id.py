from shellcheck_lib.util.textformat.structure.core import CrossReferenceTarget


class CrossReferenceId(CrossReferenceTarget):
    """
    A part of the help text that can be referred to.
    """
    pass


class ProgramCrossReferenceId(CrossReferenceId):
    pass


class TestCaseCrossReferenceId(CrossReferenceId):
    pass


class TestCasePhaseCrossReference(TestCaseCrossReferenceId):
    pass


class TestSuiteCrossReferenceId(CrossReferenceId):
    pass


class TestSuiteSectionCrossReference(TestSuiteCrossReferenceId):
    pass


class ConceptCrossReferenceId(CrossReferenceId):
    def __init__(self, concept_name: str):
        self._concept_name = concept_name

    @property
    def concept_name(self) -> str:
        return self._concept_name


class CrossReferenceIdVisitor:
    def visit(self, x: CrossReferenceId):
        if isinstance(x, ConceptCrossReferenceId):
            return self.visit_concept(x)
        else:
            raise ValueError('Not a concrete %s: %s' % (str(CrossReferenceId),
                                                        str(x)))

    def visit_concept(self, x: ConceptCrossReferenceId):
        raise NotImplementedError()
