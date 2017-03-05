import pathlib

from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure


class PreOrPostSdsValidator:
    """
    Validates an object - usually a path - either pre or post creation of SDS.

    Whether validation is done pre or post SDS depends on whether the validated
    object is outside or inside the SDS.
    """
    def validate_pre_sds_if_applicable(self, home_dir_path: pathlib.Path) -> str:
        """
        Validates the object if it is expected to exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_post_sds_if_applicable(self, sds: SandboxDirectoryStructure) -> str:
        """
        Validates the object if it is expected to NOT exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> str:
        """
        Validates the object using either pre- or post- SDS.
        :return: Error message iff validation failed.
        """
        error_message = self.validate_pre_sds_if_applicable(home_and_sds.home_dir_path)
        if error_message is not None:
            return error_message
        return self.validate_post_sds_if_applicable(home_and_sds.sds)


class ConstantSuccessValidator(PreOrPostSdsValidator):
    def validate_pre_sds_if_applicable(self, home_dir_path: pathlib.Path) -> str:
        return None

    def validate_post_sds_if_applicable(self, sds: SandboxDirectoryStructure) -> str:
        return None


class AndValidator(PreOrPostSdsValidator):
    def __init__(self,
                 validators: iter):
        self.validators = validators

    def validate_pre_sds_if_applicable(self, home_dir_path: pathlib.Path) -> str:
        for validator in self.validators:
            result = validator.validate_pre_sds_if_applicable(home_dir_path)
            if result is not None:
                return result
        return None

    def validate_post_sds_if_applicable(self, sds: SandboxDirectoryStructure) -> str:
        for validator in self.validators:
            result = validator.validate_post_sds_if_applicable(sds)
            if result is not None:
                return result
        return None


class PreOrPostSdsSvhValidationErrorValidator:
    """
    A validator that translates error messages to a svh.ValidationError
    """

    def __init__(self,
                 validator: PreOrPostSdsValidator):
        self.validator = validator

    def validate_pre_sds_if_applicable(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        return self._translate(self.validator.validate_pre_sds_if_applicable(home_dir_path))

    def validate_post_sds_if_applicable(self,
                                        sds: SandboxDirectoryStructure) -> svh.SuccessOrValidationErrorOrHardError:
        return self._translate(self.validator.validate_post_sds_if_applicable(sds))

    def validate_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> svh.SuccessOrValidationErrorOrHardError:
        return self._translate(self.validator.validate_pre_or_post_sds(home_and_sds))

    @staticmethod
    def _translate(error_message_or_none: str) -> svh.SuccessOrValidationErrorOrHardError:
        if error_message_or_none is not None:
            return svh.new_svh_validation_error(error_message_or_none)
        return svh.new_svh_success()


class PreOrPostSdsSvhValidationForSuccessOrHardError:
    """
    A validator that translates error messages to a sh.HardError
    """

    def __init__(self,
                 validator: PreOrPostSdsValidator):
        self.validator = validator

    def validate_pre_sds_if_applicable(self, home_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return self._translate(self.validator.validate_pre_sds_if_applicable(home_dir_path))

    def validate_post_sds_if_applicable(self, sds: SandboxDirectoryStructure) -> sh.SuccessOrHardError:
        return self._translate(self.validator.validate_post_sds_if_applicable(sds))

    def validate_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> sh.SuccessOrHardError:
        return self._translate(self.validator.validate_pre_or_post_sds(home_and_sds))

    @staticmethod
    def _translate(error_message_or_none: str) -> sh.SuccessOrHardError:
        if error_message_or_none is not None:
            return sh.new_sh_hard_error(error_message_or_none)
        return sh.new_sh_success()
