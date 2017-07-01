from exactly_lib.execution.result import FailureInfo
from exactly_lib.symbol.concrete_restrictions import FailureOfDirectReference, FailureOfIndirectReference


def error_message(failure: FailureInfo) -> str:
    """
    Renders an error for presentation to the user
    """
    if isinstance(failure, FailureOfDirectReference):
        return failure.error_message
    elif isinstance(failure, FailureOfIndirectReference):
        return failure.error_message
