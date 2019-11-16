import unittest
from typing import Callable, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds, \
    PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPostSds, PathResolvingEnvironment
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case_utils.test_resources.validation import Expectation, ValidationExpectation, \
    ValidationActual
from exactly_lib_test.test_resources.actions import do_nothing
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase, \
    MessageBuilder


def check(put: unittest.TestCase,
          validator: PreOrPostSdsValidator,
          environment: PathResolvingEnvironmentPreOrPostSds,
          expectation: Expectation):
    def _check(f: Callable[[PathResolvingEnvironment], Optional[TextRenderer]],
               message: str,
               expect_none: bool,
               arg):
        if expect_none:
            put.assertIsNone(f(arg),
                             message)
        else:
            put.assertIsNotNone(f(arg),
                                message)

    _check(validator.validate_pre_sds_if_applicable,
           'Validation pre SDS',
           expectation.passes_pre_sds,
           environment)
    _check(validator.validate_post_sds_if_applicable,
           'Validation post SDS',
           expectation.passes_post_sds,
           environment)
    _check(validator.validate_pre_or_post_sds,
           'Validation pre or post SDS',
           expectation.passes_pre_sds and expectation.passes_post_sds,
           environment)


class ValidatorThat(PreOrPostSdsValidator):
    def __init__(self,
                 pre_sds_action=do_nothing,
                 pre_sds_return_value: Optional[TextRenderer] = None,
                 post_setup_action=do_nothing,
                 post_setup_return_value: Optional[TextRenderer] = None,
                 ):
        self.post_setup_return_value = post_setup_return_value
        self.pre_sds_return_value = pre_sds_return_value
        self.post_setup_action = post_setup_action
        self.pre_sds_action = pre_sds_action

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        self.pre_sds_action(environment)
        return self.pre_sds_return_value

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        self.post_setup_action(environment)
        return self.post_setup_return_value


def constant_validator(result: ValidationActual) -> PreOrPostSdsValidator:
    return ValidatorThat(
        pre_sds_return_value=asrt_text_doc.new_single_string_text_for_test__optional(result.pre_sds),
        post_setup_return_value=asrt_text_doc.new_single_string_text_for_test__optional(result.post_sds),
    )


class PreOrPostSdsValidatorAssertion(ValueAssertionBase[PreOrPostSdsValidator]):
    def __init__(self,
                 expectation: ValidationExpectation,
                 environment: PathResolvingEnvironmentPreOrPostSds):
        self.expectation = expectation
        self.environment = environment

    def _apply(self,
               put: unittest.TestCase,
               value: PreOrPostSdsValidator,
               message_builder: MessageBuilder):
        pre_sds_result = value.validate_pre_sds_if_applicable(self.environment)
        self.expectation.pre_sds.apply_with_message(put,
                                                    pre_sds_result,
                                                    'pre sds validation')

        if pre_sds_result is None:
            post_sds_result = value.validate_post_sds_if_applicable(self.environment)
            self.expectation.post_sds.apply_with_message(put,
                                                         post_sds_result,
                                                         'post sds validation')


class PreOrPostSdsValidationAssertion(ValueAssertionBase[PreOrPostSdsValidator]):
    def __init__(self,
                 symbols: SymbolTable,
                 tcds: Tcds,
                 expectation: ValidationExpectation,
                 ):
        self.symbols = symbols
        self.tcds = tcds
        self.expectation = expectation

    def _apply(self,
               put: unittest.TestCase,
               value: PreOrPostSdsValidator,
               message_builder: MessageBuilder):
        environment = PathResolvingEnvironmentPreOrPostSds(self.tcds, self.symbols)

        validation_result = value.validate_pre_sds_if_applicable(environment)
        self.expectation.pre_sds.apply_with_message(put,
                                                    validation_result,
                                                    message_builder.apply('pre sds validation'))
        if validation_result is None:
            validation_result = value.validate_post_sds_if_applicable(environment)
            self.expectation.post_sds.apply_with_message(put,
                                                         validation_result,
                                                         message_builder.apply('post sds validation'))
