from typing import Optional

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure


class PreOrPostSdsValueValidator:
    """
    EXPERIMENTING WITH VALIDATOR THAT IS RESOLVED À LA SYMBOL VALUE.

    Validates an object - either pre or post creation of SDS.

    Symbols are expected to have been resolved at an earlier step.

    Whether validation is done pre or post SDS depends on whether the validated
    object is outside or inside the SDS.
    """

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[str]:
        """
        Validates the object if it is expected to exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_post_sds_if_applicable(self, tcds: HomeAndSds) -> Optional[str]:
        """
        Validates the object if it is expected to NOT exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_or_post_sds(self, tcds: HomeAndSds) -> Optional[str]:
        """
        Validates the object using either pre- or post- SDS.
        :return: Error message iff validation failed.
        """
        error_message = self.validate_pre_sds_if_applicable(tcds.hds)
        if error_message is not None:
            return error_message
        return self.validate_post_sds_if_applicable(tcds)


class ConstantPreOrPostSdsValueValidator(PreOrPostSdsValueValidator):
    def __init__(self,
                 pre_sds_result: Optional[str] = None,
                 post_sds_result: Optional[str] = None):
        self._pre_sds_result = pre_sds_result
        self._post_sds_result = post_sds_result

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[str]:
        return self._pre_sds_result

    def validate_post_sds_if_applicable(self, tcds: HomeAndSds) -> Optional[str]:
        return self._post_sds_result
