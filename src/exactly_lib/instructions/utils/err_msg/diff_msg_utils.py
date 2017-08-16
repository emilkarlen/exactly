from exactly_lib.instructions.utils.err_msg import diff_msg
from exactly_lib.instructions.utils.err_msg.property_description import PropertyDescriptor
from exactly_lib.instructions.utils.expectation_type import ExpectationType
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh


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
                 expected: str,
                 ):
        self.property_descriptor = property_descriptor
        self.expectation_type = expectation_type
        self.expected = expected

    def resolve(self,
                environment: InstructionEnvironmentForPostSdsStep,
                actual: diff_msg.ActualInfo) -> diff_msg.DiffFailureInfo:
        return diff_msg.DiffFailureInfo(
            self.property_descriptor.description(environment),
            self.expectation_type,
            self.expected,
            actual)

    def resolve_str(self,
                    environment: InstructionEnvironmentForPostSdsStep,
                    actual: diff_msg.ActualInfo) -> str:
        return self.resolve(environment, actual).render()

    def resolve_pfh_fail(self,
                         environment: InstructionEnvironmentForPostSdsStep,
                         actual: diff_msg.ActualInfo) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_fail(self.resolve_str(environment, actual))
