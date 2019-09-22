from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.matcher.matcher import Failure
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.err_msg.prop_descr import PropertyDescriptor


class ErrorMessageResolverForFailure(ErrorMessageResolver):
    def __init__(self,
                 property_descriptor: PropertyDescriptor,
                 failure: Failure[int]):
        self.property_descriptor = property_descriptor
        self.failure = failure

    def resolve(self) -> str:
        return self.failure_info().error_message()

    def failure_info(self) -> diff_msg.DiffErrorInfo:
        return diff_msg.DiffErrorInfo(
            self.property_descriptor.description(),
            self.failure.expectation_type,
            self.failure.expected,
            diff_msg.actual_with_single_line_value(str(self.failure.actual))
        )
