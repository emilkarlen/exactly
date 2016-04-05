from shellcheck_lib.util.textformat.structure.core import CrossReferenceTarget


class CrossReferenceId(CrossReferenceTarget):
    """
    A part of the help text that can be referred to.
    """
    pass


class CustomCrossReferenceId(CrossReferenceId):
    def __init__(self, target_name: str):
        self.target_name = target_name


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
        if isinstance(x, CustomCrossReferenceId):
            return self.visit_custom(x)
        else:
            raise TypeError('Not a concrete %s: %s' % (str(CrossReferenceId),
                                                       str(x)))

    def visit_concept(self, x: ConceptCrossReferenceId):
        raise NotImplementedError()

    def visit_custom(self, x: CustomCrossReferenceId):
        raise NotImplementedError()
