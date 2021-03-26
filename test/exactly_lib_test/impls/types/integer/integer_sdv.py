import unittest
from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.exception.svh_exception import SvhValidationException
from exactly_lib.impls.types.integer import integer_sdv as sut
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_case.test_resources import instruction_environment
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.type_val_deps.test_resources.validation import validation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValidationPreSds),
    ])


class CustomValidator:
    def __init__(self, value_that_makes_the_validation_succeed: int,
                 error_message: TextRenderer):
        self.error_message = error_message
        self.value_that_makes_the_validation_succeed = value_that_makes_the_validation_succeed

    def __call__(self, value: int) -> Optional[TextRenderer]:
        if value != self.value_that_makes_the_validation_succeed:
            return self.error_message

        return None


class TestValidationPreSds(unittest.TestCase):
    def test_validation_SHOULD_fail_WHEN_resolved_value_is_not_an_integer(self):

        the_instruction_environment = instruction_environment.fake_pre_sds_environment()
        test_cases = [
            'a',
            '1+x',
            'a b',
            '10 a',
            '10a',
            '1.5',
        ]
        for custom_validator in [None, do_return(None)]:
            for resolved_value in test_cases:
                with self.subTest(
                        custom_validator_is_none=str(custom_validator is None),
                        resolved_value=resolved_value):
                    # ARRANGE #
                    sdv_to_check = sut.IntegerSdv(string_sdvs.str_constant(resolved_value),
                                                  custom_validator)
                    with self.subTest(tested_obect='sdv'):
                        # ACT & ASSERT #
                        with self.assertRaises(SvhValidationException) as cm:
                            sdv_to_check.validate_pre_sds(the_instruction_environment.path_resolving_environment)

                        asrt_text_doc.is_any_text().apply_without_message(self, cm.exception.err_msg)

                    with self.subTest(tested_obect='value'):
                        # ACT & ASSERT #
                        value_to_check = sdv_to_check.resolve(the_instruction_environment.symbols)

                        actual = value_to_check.validator().validate_pre_sds_if_applicable(
                            the_instruction_environment.hds)

                        asrt_text_doc.is_any_text().apply_without_message(self, actual)

    def test_validation_SHOULD_fail_WHEN_custom_validator_fails(self):

        the_instruction_environment = instruction_environment.fake_pre_sds_environment()

        resolved_value = 1

        # ARRANGE #
        error_message_from_custom_validator = 'error message'
        sdv_to_check = sut.IntegerSdv(
            string_sdvs.str_constant(str(resolved_value)),
            CustomValidator(
                value_that_makes_the_validation_succeed=resolved_value + 1,
                error_message=validation.new_single_string_text_for_test(error_message_from_custom_validator)
            )
        )

        with self.subTest(tested_obect='sdv'):
            # ACT & ASSERT #
            with self.assertRaises(SvhValidationException) as cm:
                sdv_to_check.validate_pre_sds(the_instruction_environment.path_resolving_environment)

            err_msg_expectation = asrt_text_doc.is_string_for_test_that_equals(
                error_message_from_custom_validator
            )
            err_msg_expectation.apply_without_message(self, cm.exception.err_msg)

        with self.subTest(tested_obect='value'):
            # ACT & ASSERT #
            value_to_check = sdv_to_check.resolve(the_instruction_environment.symbols)
            actual = value_to_check.validator().validate_pre_sds_if_applicable(the_instruction_environment.hds)

            err_msg_expectation = asrt_text_doc.is_string_for_test_that_equals(
                error_message_from_custom_validator
            )
            err_msg_expectation.apply_without_message(self, actual)

    def test_validation_SHOULD_succeed_WHEN_value_is_an_integer_and_custom_validator_succeeds(self):

        the_instruction_environment = instruction_environment.fake_pre_sds_environment()

        resolved_value = 16

        resolved_string_value_cases = [
            '16',
            '8 + 8',
            '2 * 2 * 2 * 2',
        ]

        custom_validator_cases = [
            None,
            CustomValidator(
                value_that_makes_the_validation_succeed=resolved_value,
                error_message=validation.new_single_string_text_for_test('error message from custom validator')
            )
        ]
        for value_string in resolved_string_value_cases:
            for custom_validator in custom_validator_cases:
                sdv_to_check = sut.IntegerSdv(
                    string_sdvs.str_constant(str(value_string)),
                    custom_validator
                )
                with self.subTest(custom_validator_is_none=str(custom_validator is None),
                                  value_string=value_string):
                    with self.subTest(tested_obect='sdv'):
                        sdv_to_check.validate_pre_sds(the_instruction_environment.path_resolving_environment)

                    with self.subTest(tested_obect='value'):
                        value_to_check = sdv_to_check.resolve(the_instruction_environment.symbols)
                        value_to_check.validator().validate_pre_sds_if_applicable(the_instruction_environment.hds)
                        value_to_check.validator().validate_post_sds_if_applicable(fake_tcds())
