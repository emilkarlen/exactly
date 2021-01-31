import unittest

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions, Expectation
from exactly_lib_test.test_resources.value_assertions.value_assertion import AssertionBase, MessageBuilder, \
    Assertion


class DdvValidationAssertion(AssertionBase[DdvValidator]):
    def __init__(self,
                 tcds: TestCaseDs,
                 expectation: ValidationAssertions,
                 ):
        self.tcds = tcds
        self.expectation = expectation

    @staticmethod
    def of_expectation(expectation: Expectation,
                       tcds: TestCaseDs,
                       ) -> Assertion[DdvValidator]:
        return DdvValidationAssertion(tcds, ValidationAssertions.of_expectation(expectation))

    def _apply(self,
               put: unittest.TestCase,
               value: DdvValidator,
               message_builder: MessageBuilder):
        validation_result = value.validate_pre_sds_if_applicable(self.tcds.hds)
        self.expectation.pre_sds.apply_with_message(put,
                                                    validation_result,
                                                    message_builder.apply('pre sds validation'))
        if validation_result is None:
            validation_result = value.validate_post_sds_if_applicable(self.tcds)
            self.expectation.post_sds.apply_with_message(put,
                                                         validation_result,
                                                         message_builder.apply('post sds validation'))
