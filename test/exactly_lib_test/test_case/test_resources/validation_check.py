import unittest
from typing import Optional

from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomeOrSdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Arrangement:
    def __init__(self,
                 dir_contents: HomeOrSdsPopulator = home_and_sds_populators.empty,
                 symbols: SymbolTable = None):
        self.dir_contents = dir_contents
        self.symbols = symbols


class Expectation:
    def __init__(self,
                 pre_sds: asrt.ValueAssertion[Optional[str]],
                 post_sds: asrt.ValueAssertion[Optional[str]]):
        self.pre_sds = pre_sds
        self.post_sds = post_sds


def is_success() -> Expectation:
    return Expectation(asrt.is_none,
                       asrt.is_none)


def fails_on(step: ResolvingDependency) -> Expectation:
    if step is ResolvingDependency.HOME:
        return fails_pre_sds()
    else:
        return fails_post_sds()


def fails_pre_sds() -> Expectation:
    return Expectation(asrt.is_instance(str),
                       asrt.is_none)


def fails_post_sds() -> Expectation:
    return Expectation(asrt.is_none,
                       asrt.is_instance(str))


def assert_with_files(arrangement: Arrangement,
                      expectation: Expectation) -> asrt.ValueAssertion[PreOrPostSdsValidator]:
    return ValidatorAssertion(arrangement, expectation)


class ValidationCase:
    def __init__(self,
                 name: str,
                 dir_contents_before_validation: HomeOrSdsPopulator,
                 expectation: Expectation):
        self.name = name
        self.dir_contents_before_validation = dir_contents_before_validation
        self.expectation = expectation


class ValidatorAssertion(asrt.ValueAssertion[PreOrPostSdsValidator]):
    def __init__(self,
                 arrangement: Arrangement,
                 expectation: Expectation):
        self.arrangement = arrangement
        self.expectation = expectation

    def apply(self,
              put: unittest.TestCase,
              value: PreOrPostSdsValidator,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        check(put, value, self.arrangement, self.expectation, message_builder)


def check(put: unittest.TestCase,
          actual: PreOrPostSdsValidator,
          arrangement: Arrangement,
          expectation: Expectation,
          message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
    with home_and_sds_with_act_as_curr_dir(
            home_or_sds_contents=arrangement.dir_contents,
            symbols=arrangement.symbols) as path_resolving_environment:
        actual_validation_result = actual.validate_pre_sds_if_applicable(path_resolving_environment)
        expectation.pre_sds.apply(put,
                                  actual_validation_result,
                                  message_builder.for_sub_component('validation pre sds'))
        if actual_validation_result is not None:
            return
        actual_validation_result = actual.validate_post_sds_if_applicable(path_resolving_environment)
        expectation.post_sds.apply(put,
                                   actual_validation_result,
                                   message_builder.for_sub_component('validation post sds'))
