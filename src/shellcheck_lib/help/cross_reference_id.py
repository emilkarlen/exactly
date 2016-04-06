from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure.core import CrossReferenceTarget
from shellcheck_lib.util.textformat.structure.structures import text, anchor_text


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


class TargetInfo(tuple):
    def __new__(cls,
                presentation: str,
                target: core.CrossReferenceTarget):
        return tuple.__new__(cls, (presentation, target))

    @property
    def presentation_str(self) -> str:
        return self[0]

    @property
    def presentation_text(self) -> core.ConcreteText:
        return text(self[0])

    @property
    def target(self) -> core.CrossReferenceTarget:
        return self[1]

    def anchor_text(self) -> core.Text:
        return anchor_text(self.presentation_text,
                           self.target)


class CustomTargetInfoFactory:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def make(self,
             presentation: str,
             local_target_name: str) -> TargetInfo:
        return TargetInfo(presentation,
                          CustomCrossReferenceId(self.prefix + local_target_name))


def sub_component_factory(local_name: str,
                          root: CustomTargetInfoFactory) -> CustomTargetInfoFactory:
    return CustomTargetInfoFactory(root.prefix + '.' + local_name)
