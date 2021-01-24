from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.tcds import TestCaseDs


class DdvValidator:
    """
    Validates an object - either pre or post creation of SDS.

    Symbols are expected to have been resolved at an earlier step.

    Whether validation is done pre or post SDS depends on whether the validated
    object is outside or inside the SDS.
    """

    def validate_pre_sds_if_applicable(self, hds: HomeDs) -> Optional[TextRenderer]:
        """
        Validates the object if it is expected to exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_post_sds_if_applicable(self, tcds: TestCaseDs) -> Optional[TextRenderer]:
        """
        Validates the object if it is expected to NOT exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()


class ConstantDdvValidator(DdvValidator):
    def __init__(self,
                 pre_sds_result: Optional[TextRenderer] = None,
                 post_sds_result: Optional[TextRenderer] = None):
        self._pre_sds_result = pre_sds_result
        self._post_sds_result = post_sds_result

    @staticmethod
    def new_success() -> DdvValidator:
        return ConstantDdvValidator(None, None)

    @staticmethod
    def of_pre_sds(result: Optional[TextRenderer]) -> DdvValidator:
        return ConstantDdvValidator(result, None)

    @staticmethod
    def of_post_sds(result: Optional[TextRenderer]) -> DdvValidator:
        return ConstantDdvValidator(None, result)

    def validate_pre_sds_if_applicable(self, hds: HomeDs) -> Optional[TextRenderer]:
        return self._pre_sds_result

    def validate_post_sds_if_applicable(self, tcds: TestCaseDs) -> Optional[TextRenderer]:
        return self._post_sds_result
