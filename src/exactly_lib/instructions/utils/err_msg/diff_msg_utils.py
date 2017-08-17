from exactly_lib.instructions.utils.err_msg import diff_msg
from exactly_lib.instructions.utils.err_msg.property_description import PropertyDescriptor, ErrorMessagePartConstructor
from exactly_lib.instructions.utils.expectation_type import ExpectationType
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep


class ExplanationFailureInfoResolver:
    """
    Helper for constructing a :class:`diff_msg.ExplanationFailureInfo`.

    Sets some properties that are usually known early,
    and then resolves the value given properties that
    are usually only known later.
    """

    def __init__(self, object_descriptor: ErrorMessagePartConstructor):
        """
        :param object_descriptor: Describes the object that the failure relates to.
        """
        self.object_descriptor = object_descriptor

    def resolve(self,
                environment: InstructionEnvironmentForPostSdsStep,
                explanation: str) -> diff_msg.ExplanationFailureInfo:
        return diff_msg.ExplanationFailureInfo(explanation,
                                               self.object_descriptor.lines(environment))


class ExpectedValueResolver:
    def resolve(self, environment: InstructionEnvironmentForPostSdsStep) -> str:
        raise NotImplementedError('abstract method')


class ConstantExpectedValueResolver(ExpectedValueResolver):
    def __init__(self, value: str):
        self.value = value

    def resolve(self, environment: InstructionEnvironmentForPostSdsStep) -> str:
        return self.value


def expected_constant(value: str) -> ExpectedValueResolver:
    return ConstantExpectedValueResolver(value)


class DiffFailureInfoResolver:
    """
    Helper for constructing a :class:`diff_msg.DiffFailureInfo`.

    Sets some properties that are usually known early,
    and then resolves the value given properties that
    are usually only known later.
    """

    def __init__(self,
                 property_descriptor: PropertyDescriptor,
                 expectation_type: ExpectationType,
                 expected: ExpectedValueResolver,
                 ):
        """
        :param property_descriptor:  Describes the property that the failure relates to.
        :param expectation_type: if the check is positive or negative
        :param expected: single line description of the expected value (for positive ExpectationType)
        """
        self.property_descriptor = property_descriptor
        self.expectation_type = expectation_type
        self.expected = expected

    def resolve(self,
                environment: InstructionEnvironmentForPostSdsStep,
                actual: diff_msg.ActualInfo) -> diff_msg.DiffFailureInfo:
        return diff_msg.DiffFailureInfo(
            self.property_descriptor.description(environment),
            self.expectation_type,
            self.expected.resolve(environment),
            actual)
