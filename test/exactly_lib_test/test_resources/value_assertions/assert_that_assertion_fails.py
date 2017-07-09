from exactly_lib_test.test_resources import test_of_test_resources_util as test_utils
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def assert_that_assertion_fails(assertion: asrt.ValueAssertion,
                                actual):
    put = test_utils.test_case_with_failure_exception_set_to_test_exception()
    with put.assertRaises(test_utils.TestException):
        assertion.apply_without_message(put, actual)
