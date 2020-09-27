import unittest

from exactly_lib.tcfs.ddv_validation import DdvValidator
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib_test.tcfs.test_resources import tcds_populators
from exactly_lib_test.tcfs.test_resources.dir_populator import TcdsPopulator
from exactly_lib_test.tcfs.test_resources.ds_construction import tcds_with_act_as_curr_dir_2
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationResultAssertion
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


class Arrangement:
    def __init__(self,
                 dir_contents: TcdsPopulator = tcds_populators.empty,
                 ):
        self.dir_contents = dir_contents


class Expectation:
    def __init__(self,
                 pre_sds: ValidationResultAssertion,
                 post_sds: ValidationResultAssertion):
        self.pre_sds = pre_sds
        self.post_sds = post_sds


def is_success() -> Expectation:
    return Expectation(asrt.is_none,
                       asrt.is_none)


def fails_on(step: DirectoryStructurePartition) -> Expectation:
    if step is DirectoryStructurePartition.HDS:
        return fails_pre_sds()
    else:
        return fails_post_sds()


def fails_pre_sds() -> Expectation:
    return Expectation(asrt_validation.is_arbitrary_validation_failure(),
                       asrt.is_none)


def fails_post_sds() -> Expectation:
    return Expectation(asrt.is_none,
                       asrt_validation.is_arbitrary_validation_failure())


def assert_with_files(arrangement: Arrangement,
                      expectation: Expectation) -> ValueAssertion[DdvValidator]:
    return ValidatorAssertion(arrangement, expectation)


class ValidationCase:
    def __init__(self,
                 name: str,
                 dir_contents_before_validation: TcdsPopulator,
                 expectation: Expectation):
        self.name = name
        self.dir_contents_before_validation = dir_contents_before_validation
        self.expectation = expectation


class ValidatorAssertion(ValueAssertionBase[DdvValidator]):
    def __init__(self,
                 arrangement: Arrangement,
                 expectation: Expectation):
        self.arrangement = arrangement
        self.expectation = expectation

    def _apply(self,
               put: unittest.TestCase,
               value: DdvValidator,
               message_builder: asrt.MessageBuilder):
        check(put, value, self.arrangement, self.expectation, message_builder)


def check(put: unittest.TestCase,
          actual: DdvValidator,
          arrangement: Arrangement,
          expectation: Expectation,
          message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
    with tcds_with_act_as_curr_dir_2(
            tcds_contents=arrangement.dir_contents) as tcds:
        actual_validation_result = actual.validate_pre_sds_if_applicable(tcds.hds)
        expectation.pre_sds.apply(put,
                                  actual_validation_result,
                                  message_builder.for_sub_component('validation pre sds'))
        if actual_validation_result is not None:
            return
        actual_validation_result = actual.validate_post_sds_if_applicable(tcds)
        expectation.post_sds.apply(put,
                                   actual_validation_result,
                                   message_builder.for_sub_component('validation post sds'))
