from enum import Enum

from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import EntityTypeNames
from exactly_lib.util.textformat.structure.core import CrossReferenceTarget, UrlCrossReferenceTarget


class CustomCrossReferenceId(CrossReferenceId):
    def __init__(self, target_name: str):
        self._target_name = target_name

    @property
    def target_name(self) -> str:
        return self._target_name

    def _eq_object_of_same_type(self, other):
        return self._target_name == other.target_name


class TestCaseCrossReferenceId(CrossReferenceId):
    pass


class TestCasePhaseCrossReferenceBase(TestCaseCrossReferenceId):
    def __init__(self, phase_name: str):
        self._phase_name = phase_name

    @property
    def phase_name(self) -> str:
        return self._phase_name

    def _eq_object_of_same_type(self, other):
        return self.phase_name == other.phase_name and self._eq_object_of_same_phase(other)

    def _eq_object_of_same_phase(self, other):
        raise NotImplementedError('abstract method')


class TestCasePhaseCrossReference(TestCasePhaseCrossReferenceBase):
    def _eq_object_of_same_phase(self, other):
        return True


class TestCasePhaseInstructionCrossReference(TestCasePhaseCrossReferenceBase):
    def __init__(self,
                 phase_name: str,
                 instruction_name: str):
        super().__init__(phase_name)
        self._instruction_name = instruction_name

    @property
    def instruction_name(self) -> str:
        return self._instruction_name

    def _eq_object_of_same_phase(self, other):
        return self.instruction_name == other.instruction_name


class TestSuiteCrossReferenceId(CrossReferenceId):
    pass


class TestSuiteSectionCrossReferenceBase(TestSuiteCrossReferenceId):
    def __init__(self, section_name: str):
        self._section_name = section_name

    @property
    def section_name(self) -> str:
        return self._section_name

    def _eq_object_of_same_type(self, other):
        return self._section_name == other._section_name and self._eq_object_of_same_section(other)

    def _eq_object_of_same_section(self, other):
        raise NotImplementedError('abstract method')


class TestSuiteSectionCrossReference(TestSuiteSectionCrossReferenceBase):
    def _eq_object_of_same_section(self, other):
        return True


class TestSuiteSectionInstructionCrossReference(TestSuiteSectionCrossReferenceBase):
    def __init__(self,
                 section_name: str,
                 instruction_name: str):
        super().__init__(section_name)
        self._instruction_name = instruction_name

    @property
    def instruction_name(self) -> str:
        return self._instruction_name

    def _eq_object_of_same_section(self, other):
        return self._instruction_name == other.instruction_name


class EntityCrossReferenceId(CrossReferenceId):
    def __init__(self,
                 entity_type_names: EntityTypeNames,
                 entity_name: str):
        self._entity_type_names = entity_type_names
        self._entity_name = entity_name

    @property
    def entity_type_names(self) -> EntityTypeNames:
        return self._entity_type_names

    @property
    def entity_type_identifier(self) -> str:
        return self._entity_type_names.identifier

    @property
    def entity_type_presentation_name(self) -> str:
        return self._entity_type_names.name.singular

    @property
    def entity_name(self) -> str:
        return self._entity_name

    def _eq_object_of_same_type(self, other):
        return self.entity_type_identifier == other.entity_type_identifier and \
               self.entity_type_presentation_name == other.entity_type_presentation_name and \
               self.entity_name == other.entity_name


class HelpPredefinedContentsPart(Enum):
    TEST_CASE_CLI = 1
    TEST_SUITE_CLI = 2
    SYMBOL_CLI = 3
    TEST_CASE_SPEC = 10
    TEST_SUITE_SPEC = 11


class PredefinedHelpContentsPartReference(CrossReferenceId):
    def __init__(self, part: HelpPredefinedContentsPart):
        self._part = part

    @property
    def part(self) -> HelpPredefinedContentsPart:
        return self._part

    def _eq_object_of_same_type(self, other):
        assert isinstance(other, PredefinedHelpContentsPartReference)

        return self._part is other._part


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
        if isinstance(x, PredefinedHelpContentsPartReference):
            return self.visit_predefined_part(x)
        else:
            raise TypeError('Not a concrete %s: %s' % (str(CrossReferenceTarget),
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

    def visit_predefined_part(self, x: PredefinedHelpContentsPartReference):
        raise NotImplementedError()
