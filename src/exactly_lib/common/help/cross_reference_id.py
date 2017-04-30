from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.core import CrossReferenceTarget, UrlCrossReferenceTarget
from exactly_lib.util.textformat.structure.structures import text, anchor_text


class CrossReferenceId(CrossReferenceTarget):
    """
    A part of the help text that can be referred to.
    """
    pass


class CustomCrossReferenceId(CrossReferenceId):
    def __init__(self, target_name: str):
        self._target_name = target_name

    @property
    def target_name(self) -> str:
        return self._target_name


class TestCaseCrossReferenceId(CrossReferenceId):
    pass


class TestCasePhaseCrossReferenceBase(TestCaseCrossReferenceId):
    def __init__(self, phase_name: str):
        self._phase_name = phase_name

    @property
    def phase_name(self) -> str:
        return self._phase_name


class TestCasePhaseCrossReference(TestCasePhaseCrossReferenceBase):
    pass


class TestCasePhaseInstructionCrossReference(TestCasePhaseCrossReferenceBase):
    def __init__(self,
                 phase_name: str,
                 instruction_name: str):
        super().__init__(phase_name)
        self._instruction_name = instruction_name

    @property
    def instruction_name(self) -> str:
        return self._instruction_name


class TestSuiteCrossReferenceId(CrossReferenceId):
    pass


class TestSuiteSectionCrossReferenceBase(TestSuiteCrossReferenceId):
    def __init__(self, section_name: str):
        self._section_name = section_name

    @property
    def section_name(self) -> str:
        return self._section_name


class TestSuiteSectionCrossReference(TestSuiteSectionCrossReferenceBase):
    pass


class TestSuiteSectionInstructionCrossReference(TestSuiteSectionCrossReferenceBase):
    def __init__(self,
                 section_name: str,
                 instruction_name: str):
        super().__init__(section_name)
        self._instruction_name = instruction_name

    @property
    def instruction_name(self) -> str:
        return self._instruction_name


class EntityCrossReferenceId(CrossReferenceId):
    def __init__(self,
                 entity_type_name: str,
                 entity_name: str):
        self._entity_type_name = entity_type_name
        self._entity_name = entity_name

    @property
    def entity_type_name(self) -> str:
        return self._entity_type_name

    @property
    def entity_name(self) -> str:
        return self._entity_name


class CrossReferenceIdVisitor:
    def visit(self, x: CrossReferenceTarget):
        if isinstance(x, CustomCrossReferenceId):
            return self.visit_custom(x)
        if isinstance(x, TestCasePhaseCrossReference):
            return self.visit_test_case_phase(x)
        if isinstance(x, TestCasePhaseInstructionCrossReference):
            return self.visit_test_case_phase_instruction(x)
        if isinstance(x, TestSuiteSectionCrossReference):
            return self.visit_test_suite_section(x)
        if isinstance(x, TestSuiteSectionInstructionCrossReference):
            return self.visit_test_suite_section_instruction(x)
        if isinstance(x, EntityCrossReferenceId):
            return self.visit_entity(x)
        if isinstance(x, UrlCrossReferenceTarget):
            return self.visit_url(x)
        else:
            raise TypeError('Not a concrete %s: %s' % (str(CrossReferenceId),
                                                       str(x)))

    def visit_entity(self, x: EntityCrossReferenceId):
        raise NotImplementedError()

    def visit_test_case_phase(self, x: TestCasePhaseCrossReference):
        raise NotImplementedError()

    def visit_test_case_phase_instruction(self, x: TestCasePhaseInstructionCrossReference):
        raise NotImplementedError()

    def visit_test_suite_section(self, x: TestSuiteSectionCrossReference):
        raise NotImplementedError()

    def visit_test_suite_section_instruction(self, x: TestSuiteSectionInstructionCrossReference):
        raise NotImplementedError()

    def visit_custom(self, x: CustomCrossReferenceId):
        raise NotImplementedError()

    def visit_url(self, x: UrlCrossReferenceTarget):
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


class TargetInfoNode(tuple):
    def __new__(cls,
                data: TargetInfo,
                children: list):
        """
        :type children: [TargetInfoNode]
        """
        return tuple.__new__(cls, (data, children))

    @property
    def data(self) -> TargetInfo:
        return self[0]

    @property
    def children(self) -> list:
        """
        :rtype [TargetInfoNode]
        """
        return self[1]


def target_info_leaf(ti: TargetInfo) -> TargetInfoNode:
    return TargetInfoNode(ti, [])


class CustomTargetInfoFactory:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def sub(self,
            presentation: str,
            local_target_name: str) -> TargetInfo:
        return TargetInfo(presentation,
                          CustomCrossReferenceId(self.prefix + _COMPONENT_SEPARATOR + local_target_name))

    def root(self, presentation: str) -> TargetInfo:
        return TargetInfo(presentation,
                          CustomCrossReferenceId(self.prefix))

    def sub_factory(self, local_name: str):
        return sub_component_factory(local_name, self)


def root_factory() -> CustomTargetInfoFactory:
    return CustomTargetInfoFactory('')


def sub_component_factory(local_name: str,
                          root: CustomTargetInfoFactory) -> CustomTargetInfoFactory:
    if not root.prefix:
        prefix = local_name
    else:
        prefix = root.prefix + _COMPONENT_SEPARATOR + local_name
    return CustomTargetInfoFactory(prefix)


_COMPONENT_SEPARATOR = '.'
