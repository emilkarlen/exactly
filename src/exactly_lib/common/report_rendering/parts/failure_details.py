from typing import Sequence

from exactly_lib.common.err_msg.msg import minors
from exactly_lib.common.report_rendering.parts import error_description as err_descr_rend
from exactly_lib.test_case import error_description
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util.simple_textstruct.rendering.components import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class FailureDetailsRenderer(SequenceRenderer[MajorBlock]):
    def __init__(self, failure_details: FailureDetails):
        self._failure_details = failure_details

    def render(self) -> Sequence[MajorBlock]:
        failure_details = self._failure_details
        if failure_details.is_only_failure_message:
            ed = error_description.of_message(
                minors.of_file_printable__opt(failure_details.failure_message)
            )
        else:
            ed = error_description.of_exception(
                failure_details.exception,
                minors.of_file_printable__opt(failure_details.failure_message)
            )

        return err_descr_rend.ErrorDescriptionRenderer(ed).render()
