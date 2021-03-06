import types
import unittest

from exactly_lib.definitions.cross_ref.concrete_cross_refs import *
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase


class _IsCrossReferenceId(AssertionBase):
    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        self._assertion_for(value).apply(put, value, message_builder)

    @staticmethod
    def _assertion_for(value) -> Assertion:
        try:
            return _IS_CROSS_REFERENCE_ID_ASSERTION_GETTER.visit(value)
        except TypeError:
            return asrt.fail('Not an instance of {}: {}'.format(CrossReferenceId, value))


is_any = _IsCrossReferenceId()


class _IsCrossReferenceTargetAssertionGetter(CrossReferenceTargetVisitor):
    def visit_entity(self, x: EntityCrossReferenceId):
        return _assertion_on_properties_of(x, entity_is_valid)

    def visit_test_case_phase(self, x: TestCasePhaseCrossReference):
        return _assertion_on_properties_of(x, test_case_phase_is_valid)

    def visit_test_case_phase_instruction(self, x: TestCasePhaseInstructionCrossReference):
        return _assertion_on_properties_of(x, test_case_phase_instruction_is_valid)

    def visit_test_suite_section(self, x: TestSuiteSectionCrossReference):
        return _assertion_on_properties_of(x, test_suite_section_is_valid)

    def visit_test_suite_section_instruction(self, x: TestSuiteSectionInstructionCrossReference):
        return _assertion_on_properties_of(x, test_suite_section_instruction_is_valid)

    def visit_custom(self, x: CustomCrossReferenceId):
        return _assertion_on_properties_of(x, custom_is_valid)

    def visit_url(self, x: UrlCrossReferenceTarget):
        return _assertion_on_properties_of(x, url_is_valid)

    def visit_predefined_part(self, x: PredefinedHelpContentsPartReference):
        return equals_predefined_contents_part(x)


def _is_str(component_name: str, component_getter: types.FunctionType) -> Assertion:
    return asrt.sub_component(component_name, component_getter, asrt.IsInstance(str))


_IS_CROSS_REFERENCE_ID_ASSERTION_GETTER = _IsCrossReferenceTargetAssertionGetter()

test_case_phase_is_valid = _is_str('phase name', TestCasePhaseCrossReference.phase_name.fget)

test_suite_section_is_valid = _is_str('section name', TestSuiteSectionCrossReference.section_name.fget)

entity_is_valid = asrt.And([
    _is_str('entity type name', EntityCrossReferenceId.entity_type_identifier.fget),
    _is_str('entity name', EntityCrossReferenceId.entity_name.fget),
])


def is_entity_for_type(entity_type_name: str) -> Assertion:
    return asrt.And([
        is_entity,
        asrt.sub_component('entity type name',
                           EntityCrossReferenceId.entity_type_identifier.fget,
                           asrt.Equals(entity_type_name))
    ])


def equals_predefined_contents_part(x: PredefinedHelpContentsPartReference) -> Assertion[CrossReferenceId]:
    return asrt.is_instance_with(PredefinedHelpContentsPartReference,
                                 asrt.sub_component('part',
                                                    PredefinedHelpContentsPartReference.part.fget,
                                                    asrt.equals(x.part))
                                 )


is_entity = asrt.is_instance_with(EntityCrossReferenceId, entity_is_valid)

test_case_phase_instruction_is_valid = asrt.And([
    _is_str('phase name', TestCasePhaseInstructionCrossReference.phase_name.fget),
    _is_str('instruction name', TestCasePhaseInstructionCrossReference.instruction_name.fget),
])

test_suite_section_instruction_is_valid = asrt.And([
    _is_str('section name', TestSuiteSectionInstructionCrossReference.section_name.fget),
    _is_str('instruction name', TestSuiteSectionInstructionCrossReference.instruction_name.fget),
])

custom_is_valid = _is_str('target name', CustomCrossReferenceId.target_name.fget)

url_is_valid = _is_str('url', UrlCrossReferenceTarget.url.fget)


def _assertion_on_properties_of(x, properties_assertion: Assertion) -> Assertion:
    return asrt.with_transformed_message(asrt.append_to_message(':' + str(type(x)) + ':'),
                                         properties_assertion)


def equals(expected: CrossReferenceId) -> Assertion:
    return _CrossReferenceIdEquals(expected)


class _CrossReferenceIdEquals(AssertionBase):
    def __init__(self, expected: CrossReferenceId):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, type(self.expected), message_builder.apply('type of CrossReferenceId'))
        equality_checker = _CrossReferenceTargetEqualsWhenClassIsEqual(self.expected, put, message_builder)
        equality_checker.visit(value)


class _CrossReferenceTargetEqualsWhenClassIsEqual(CrossReferenceTargetVisitor):
    def __init__(self,
                 expected: CrossReferenceId,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        self.put = put
        self.message_builder = message_builder
        self.expected = expected

    def visit_entity(self, x: EntityCrossReferenceId):
        assert isinstance(self.expected, EntityCrossReferenceId)
        self.put.assertEqual(self.expected.entity_type_identifier,
                             x.entity_type_identifier,
                             self.message_builder.apply('entity_type_name'))
        self.put.assertEqual(self.expected.entity_name,
                             x.entity_name,
                             self.message_builder.apply('entity_name'))

    def visit_test_case_phase(self, x: TestCasePhaseCrossReference):
        assert isinstance(self.expected, TestCasePhaseCrossReference)
        self.put.assertEqual(self.expected.phase_name,
                             x.phase_name,
                             self.message_builder.apply('phase_name'))

    def visit_test_case_phase_instruction(self, x: TestCasePhaseInstructionCrossReference):
        assert isinstance(self.expected, TestCasePhaseInstructionCrossReference)
        self.put.assertEqual(self.expected.phase_name,
                             x.phase_name,
                             self.message_builder.apply('phase_name'))
        self.put.assertEqual(self.expected.instruction_name,
                             x.instruction_name,
                             self.message_builder.apply('instruction_name'))

    def visit_test_suite_section(self, x: TestSuiteSectionCrossReference):
        assert isinstance(self.expected, TestSuiteSectionCrossReference)
        self.put.assertEqual(self.expected.section_name,
                             x.section_name,
                             self.message_builder.apply('section_name'))

    def visit_test_suite_section_instruction(self, x: TestSuiteSectionInstructionCrossReference):
        assert isinstance(self.expected, TestSuiteSectionInstructionCrossReference)
        self.put.assertEqual(self.expected.section_name,
                             x.section_name,
                             self.message_builder.apply('section_name'))
        self.put.assertEqual(self.expected.instruction_name,
                             x.instruction_name,
                             self.message_builder.apply('instruction_name'))

    def visit_custom(self, x: CustomCrossReferenceId):
        assert isinstance(self.expected, CustomCrossReferenceId)
        self.put.assertEqual(self.expected.target_name,
                             x.target_name,
                             self.message_builder.apply('target_name'))

    def visit_url(self, x: UrlCrossReferenceTarget):
        assert isinstance(self.expected, UrlCrossReferenceTarget)
        self.put.assertEqual(self.expected.url,
                             x.url,
                             self.message_builder.apply('url'))

    def visit_predefined_part(self, x: PredefinedHelpContentsPartReference):
        assert isinstance(self.expected, PredefinedHelpContentsPartReference)
        self.put.assertEqual(self.expected.part,
                             x.part,
                             self.message_builder.apply('part'))
