import unittest
from typing import TypeVar, Generic, Optional

from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation
from exactly_lib_test.test_resources.value_assertions.value_assertion import AssertionBase, MessageBuilder, \
    Assertion

T = TypeVar('T')


class AdvWvAssertionModel(Generic[T]):
    def __init__(self,
                 environment: ApplicationEnvironment,
                 adv: AdvWValidation[T],
                 ):
        self.environment = environment
        self.adv = adv


def is_valid(resolved_value: Assertion[T]) -> Assertion[AdvWvAssertionModel[T]]:
    return _IsValid(resolved_value)


def is_invalid() -> Assertion[AdvWvAssertionModel[T]]:
    return _IsInvalid()


def is_valid__optional(resolved_value: Assertion[Optional[T]]) -> Assertion[Optional[AdvWvAssertionModel[T]]]:
    return _IsInvalid()


class _IsValid(Generic[T], AssertionBase[AdvWvAssertionModel[T]]):
    def __init__(self, resolved_value: Assertion[T]):
        self._resolved_value = resolved_value

    def _apply(self,
               put: unittest.TestCase,
               value: AdvWvAssertionModel[T],
               message_builder: MessageBuilder):
        result_of_validation = value.adv.validate()
        put.assertIsNone(
            result_of_validation,
            message_builder.apply('validation result')
        )
        resolved_value = value.adv.resolve(value.environment)
        self._resolved_value.apply(
            put,
            resolved_value,
            message_builder.for_sub_component('resolved value')
        )


class _IsInvalid(Generic[T], AssertionBase[AdvWvAssertionModel[T]]):
    def _apply(self,
               put: unittest.TestCase,
               value: AdvWvAssertionModel[T],
               message_builder: MessageBuilder):
        result_of_validation = value.adv.validate()

        put.assertIsNotNone(
            result_of_validation,
            message_builder.apply('validation result')
        )
