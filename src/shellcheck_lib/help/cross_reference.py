class CrossReference:
    pass


class ProgramCrossReference(CrossReference):
    pass


class TestCaseCrossReference(CrossReference):
    pass


class TestCasePhaseCrossReference(TestCaseCrossReference):
    pass


class TestSuiteCrossReference(CrossReference):
    pass


class TestSuiteSectionCrossReference(TestSuiteCrossReference):
    pass


class ConceptCrossReference(CrossReference):
    def __init__(self, concept_name: str):
        self._concept_name = concept_name

    @property
    def concept_name(self) -> str:
        return self._concept_name
