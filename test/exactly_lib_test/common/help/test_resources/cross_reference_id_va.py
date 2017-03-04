import types
import unittest

from exactly_lib.common.help.cross_reference_id import *
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class _IsCrossReferenceId(va.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        self._assertion_for(value).apply(put, value, message_builder)

    @staticmethod
    def _assertion_for(value) -> va.ValueAssertion:
        try:
            return _IS_CROSS_REFERENCE_ID_ASSERTION_GETTER.visit(value)
        except TypeError:
            return va.fail('Not an instance of {}: {}'.format(CrossReferenceId, value))


is_any = _IsCrossReferenceId()


class _IsCrossReferenceIdAssertionGetter(CrossReferenceIdVisitor):
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


def _is_str(component_name: str, component_getter: types.FunctionType) -> va.ValueAssertion:
    return va.sub_component(component_name, component_getter, va.IsInstance(str))


_IS_CROSS_REFERENCE_ID_ASSERTION_GETTER = _IsCrossReferenceIdAssertionGetter()

test_case_phase_is_valid = _is_str('phase name', TestCasePhaseCrossReference.phase_name.fget)

test_suite_section_is_valid = _is_str('section name', TestSuiteSectionCrossReference.section_name.fget)

entity_is_valid = va.And([
    _is_str('entity type name', EntityCrossReferenceId.entity_type_name.fget),
    _is_str('entity name', EntityCrossReferenceId.entity_name.fget),
])


def is_entity_for_type(entity_type_name: str) -> va.ValueAssertion:
    return va.And([
        is_entity,
        va.sub_component('entity type name',
                         EntityCrossReferenceId.entity_type_name.fget,
                         va.Equals(entity_type_name))
    ])


is_entity = va.is_instance_with(EntityCrossReferenceId, entity_is_valid)

test_case_phase_instruction_is_valid = va.And([
    _is_str('phase name', TestCasePhaseInstructionCrossReference.phase_name.fget),
    _is_str('instruction name', TestCasePhaseInstructionCrossReference.instruction_name.fget),
])

test_suite_section_instruction_is_valid = va.And([
    _is_str('section name', TestSuiteSectionInstructionCrossReference.section_name.fget),
    _is_str('instruction name', TestSuiteSectionInstructionCrossReference.instruction_name.fget),
])

custom_is_valid = _is_str('target name', CustomCrossReferenceId.target_name.fget)

url_is_valid = _is_str('url', UrlCrossReferenceTarget.url.fget)


def _assertion_on_properties_of(x, properties_assertion: va.ValueAssertion) -> va.ValueAssertion:
    return va.with_transformed_message(va.append_to_message(':' + str(type(x)) + ':'),
                                       properties_assertion)


def equals(expected: CrossReferenceId) -> va.ValueAssertion:
    return _CrossReferenceIdEquals(expected)


class _CrossReferenceIdEquals(va.ValueAssertion):
    def __init__(self, expected: CrossReferenceId):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        put.assertIsInstance(value, type(self.expected), message_builder.apply('type of CrossReferenceId'))
        equality_checker = _CrossReferenceIdEqualsWhenClassIsEqual(self.expected, put, message_builder)
        equality_checker.visit(value)


class _CrossReferenceIdEqualsWhenClassIsEqual(CrossReferenceIdVisitor):
    def __init__(self,
                 expected: CrossReferenceId,
                 put: unittest.TestCase,
                 message_builder: va.MessageBuilder = va.MessageBuilder()):
        self.put = put
        self.message_builder = message_builder
        self.expected = expected

    def visit_entity(self, x: EntityCrossReferenceId):
        assert isinstance(self.expected, EntityCrossReferenceId)
        self.put.assertEquals(self.expected.entity_type_name,
                              x.entity_type_name,
                              self.message_builder.apply('entity_type_name'))
        self.put.assertEquals(self.expected.entity_name,
                              x.entity_name,
                              self.message_builder.apply('entity_name'))

    def visit_test_case_phase(self, x: TestCasePhaseCrossReference):
        assert isinstance(self.expected, TestCasePhaseCrossReference)
        self.put.assertEquals(self.expected.phase_name,
                              x.phase_name,
                              self.message_builder.apply('phase_name'))

    def visit_test_case_phase_instruction(self, x: TestCasePhaseInstructionCrossReference):
        assert isinstance(self.expected, TestCasePhaseInstructionCrossReference)
        self.put.assertEquals(self.expected.phase_name,
                              x.phase_name,
                              self.message_builder.apply('phase_name'))
        self.put.assertEquals(self.expected.instruction_name,
                              x.instruction_name,
                              self.message_builder.apply('instruction_name'))

    def visit_test_suite_section(self, x: TestSuiteSectionCrossReference):
        assert isinstance(self.expected, TestSuiteSectionCrossReference)
        self.put.assertEquals(self.expected.section_name,
                              x.section_name,
                              self.message_builder.apply('section_name'))

    def visit_test_suite_section_instruction(self, x: TestSuiteSectionInstructionCrossReference):
        assert isinstance(self.expected, TestSuiteSectionInstructionCrossReference)
        self.put.assertEquals(self.expected.section_name,
                              x.section_name,
                              self.message_builder.apply('section_name'))
        self.put.assertEquals(self.expected.instruction_name,
                              x.instruction_name,
                              self.message_builder.apply('instruction_name'))

    def visit_custom(self, x: CustomCrossReferenceId):
        assert isinstance(self.expected, CustomCrossReferenceId)
        self.put.assertEquals(self.expected.target_name,
                              x.target_name,
                              self.message_builder.apply('target_name'))

    def visit_url(self, x: UrlCrossReferenceTarget):
        assert isinstance(self.expected, UrlCrossReferenceTarget)
        self.put.assertEquals(self.expected.url,
                              x.url,
                              self.message_builder.apply('url'))
