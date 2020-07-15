from exactly_lib.common.report_rendering.parts import failure_details as failure_details_rendering
from exactly_lib.test_case.result import sh
from exactly_lib.test_case.result.failure_details import FailureDetails


class DetectedException(Exception):
    def __init__(self, failure_detail: FailureDetails):
        self._failure_detail = failure_detail

    @property
    def failure_details(self) -> FailureDetails:
        return self._failure_detail


def return_success_or_hard_error(callable_block, *args, **kwargs) -> sh.SuccessOrHardError:
    """
    Executes a callable (by invoking its __call__), and returns hard-error iff
    a `DetectedException` is raised, otherwise success.
    :param callable_block: 
    :param args: Arguments given to callable_block
    :param kwargs: Arguments given to callable_block
    :return: success iff callable_block does not raise `DetectedException`, otherwise success
    """
    try:
        callable_block(*args, **kwargs)
        return sh.new_sh_success()
    except DetectedException as ex:
        return sh.new_sh_hard_error(
            failure_details_rendering.FailureDetailsRenderer(ex.failure_details)
        )
