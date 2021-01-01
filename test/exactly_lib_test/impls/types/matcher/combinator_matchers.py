import enum
import unittest
from typing import TypeVar, Callable

from exactly_lib.impls.types.matcher.impls import combinator_matchers as sut
from exactly_lib.impls.types.matcher.impls import constant
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib_test.impls.types.matcher.test_resources.matcher_w_init_action import MatcherWInitialAction, \
    ActionThatAppliesAssertion2
from exactly_lib_test.test_resources.recording import SequenceRecordingMedia, ConstantRecorder
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.matcher.test_resources import matching_result
from exactly_lib_test.type_val_prims.test_resources.std_type_visitor import \
    MatcherStdTypeVisitorTestAcceptImpl, assert_argument_satisfies__and_return


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestNegation),
        unittest.makeSuite(TestConjunction),
        unittest.makeSuite(TestDisjunction),
    ])


class TestNegation(unittest.TestCase):
    def test_accept_visitor_invokes_correct_method(self):
        # ARRANGE #
        operand = constant.MatcherWithConstantResult(False)
        matcher = sut.Negation(operand)

        return_value = 5
        visitor = MatcherStdTypeVisitorTestAcceptImpl.new_w_default_to_raise_exception(
            negation_action=assert_argument_satisfies__and_return(self, asrt.is_(operand), return_value)
        )
        # ACT & ASSERT #
        actual_return_value = matcher.accept(visitor)
        # ASSERT #
        self.assertEqual(return_value, actual_return_value, 'return value')


class TestConjunction(unittest.TestCase):
    def test_accept_visitor_invokes_correct_method(self):
        # ARRANGE #
        operand1 = constant.MatcherWithConstantResult(False)
        operand2 = constant.MatcherWithConstantResult(False)
        operand3 = constant.MatcherWithConstantResult(False)
        matcher = sut.Conjunction([operand1, operand2, operand3])

        return_value = 7
        visitor = MatcherStdTypeVisitorTestAcceptImpl.new_w_default_to_raise_exception(
            conjunction_action=assert_argument_satisfies__and_return(
                self,
                asrt.matches_sequence([asrt.is_(operand1), asrt.is_(operand2), asrt.is_(operand3)]),
                return_value,
            )
        )
        actual_return_value = matcher.accept(visitor)
        # ASSERT #
        self.assertEqual(return_value, actual_return_value, 'return value')

    def test_freezer_is_applied_once_before_operand_application(self):
        # ARRANGE #
        expected_method_invocation_sequence = [
            ApplicationMethod.FREEZE,
            ApplicationMethod.OPERAND_APPLICATION,
            ApplicationMethod.OPERAND_APPLICATION,
        ]
        invocation_recordings = SequenceRecordingMedia()
        recorder_of_freeze = ConstantRecorder(ApplicationMethod.FREEZE,
                                              invocation_recordings)
        freezer = FreezerThatRecordsApplication(recorder_of_freeze.action).freeze
        recorder_of_operand_application = ConstantRecorder(ApplicationMethod.OPERAND_APPLICATION,
                                                           invocation_recordings)
        true_result = matching_result.of(True)
        operand1 = MatcherWInitialAction(recorder_of_operand_application.action,
                                         true_result)
        operand2 = MatcherWInitialAction(recorder_of_operand_application.action,
                                         true_result)
        matcher = sut.Conjunction([operand1, operand2],
                                  freezer)

        # ACT #
        matcher.matches_w_trace(0)
        # ASSERT #
        self.assertEqual(expected_method_invocation_sequence,
                         invocation_recordings.recordings,
                         'method invocation sequence')

    def test_frozen_model_is_passed_to_operands(self):
        # ARRANGE #
        operand1 = matcher_that_asserts_model_is_frozen(self, True, 'operand1')
        operand2 = matcher_that_asserts_model_is_frozen(self, True, 'operand2')
        matcher = sut.Conjunction([operand1, operand2],
                                  give_frozen_model)

        original_unfrozen_model = TestModelWFreezing(False)
        # ACT & ASSERT #
        matcher.matches_w_trace(original_unfrozen_model)


class TestDisjunction(unittest.TestCase):
    def test_accept_visitor_invokes_correct_method(self):
        # ARRANGE #
        operand1 = constant.MatcherWithConstantResult(False)
        operand2 = constant.MatcherWithConstantResult(False)
        matcher = sut.Disjunction([operand1, operand2])

        return_value = 11
        visitor = MatcherStdTypeVisitorTestAcceptImpl.new_w_default_to_raise_exception(
            disjunction_action=assert_argument_satisfies__and_return(
                self,
                asrt.matches_sequence([asrt.is_(operand1), asrt.is_(operand2)]),
                return_value,
            )
        )
        actual_return_value = matcher.accept(visitor)
        # ASSERT #
        self.assertEqual(return_value, actual_return_value, 'return value')

    def test_freezer_is_applied_once_before_operand_application(self):
        # ARRANGE #
        expected_method_invocation_sequence = [
            ApplicationMethod.FREEZE,
            ApplicationMethod.OPERAND_APPLICATION,
            ApplicationMethod.OPERAND_APPLICATION,
        ]
        invocation_recordings = SequenceRecordingMedia()
        recorder_of_freeze = ConstantRecorder(ApplicationMethod.FREEZE,
                                              invocation_recordings)
        freezer = FreezerThatRecordsApplication(recorder_of_freeze.action).freeze
        recorder_of_operand_application = ConstantRecorder(ApplicationMethod.OPERAND_APPLICATION,
                                                           invocation_recordings)
        false_result = matching_result.of(False)
        operand1 = MatcherWInitialAction(recorder_of_operand_application.action,
                                         false_result)
        operand2 = MatcherWInitialAction(recorder_of_operand_application.action,
                                         false_result)
        matcher = sut.Disjunction([operand1, operand2],
                                  freezer)

        # ACT #
        matcher.matches_w_trace(0)
        # ASSERT #
        self.assertEqual(expected_method_invocation_sequence,
                         invocation_recordings.recordings,
                         'method invocation sequence')

    def test_frozen_model_is_passed_to_operands(self):
        # ARRANGE #
        operand1 = matcher_that_asserts_model_is_frozen(self, False, 'operand1')
        operand2 = matcher_that_asserts_model_is_frozen(self, False, 'operand2')
        matcher = sut.Disjunction([operand1, operand2],
                                  give_frozen_model)

        original_unfrozen_model = TestModelWFreezing(False)
        # ACT & ASSERT #
        matcher.matches_w_trace(original_unfrozen_model)


class ApplicationMethod(enum.Enum):
    FREEZE = 1
    OPERAND_APPLICATION = 2


class TestModelWFreezing:
    def __init__(self, is_frozen: bool):
        self._is_frozen = is_frozen

    def is_frozen(self) -> bool:
        return self._is_frozen


def give_frozen_model(model: TestModelWFreezing) -> TestModelWFreezing:
    return TestModelWFreezing(True)


T = TypeVar('T')


class FreezerThatRecordsApplication:
    def __init__(self, recorder: Callable):
        self._recorder = recorder

    def freeze(self, model: T) -> T:
        self._recorder()
        return model


def matcher_that_asserts_model_is_frozen(put: unittest.TestCase,
                                         result: bool,
                                         matcher_name: str) -> MatcherWTrace[TestModelWFreezing]:
    assert_model_is_frozen = ActionThatAppliesAssertion2(
        put,
        asrt.sub_component(
            'is_frozen',
            TestModelWFreezing.is_frozen,
            asrt.equals(True)
        ),
        asrt.MessageBuilder(matcher_name)
    )
    return MatcherWInitialAction(assert_model_is_frozen.action,
                                 matching_result.of(result))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
