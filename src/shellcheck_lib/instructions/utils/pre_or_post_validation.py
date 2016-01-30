import pathlib

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.test_case.phases.common import HomeAndEds
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.test_case.phases.result import svh


class PreOrPostEdsValidator:
    def validate_pre_eds_if_applicable(self, home_dir_path: pathlib.Path) -> str:
        """
        Validates the object if it is expected to exist pre-EDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_post_eds_if_applicable(self, eds: ExecutionDirectoryStructure) -> str:
        """
        Validates the object if it is expected to NOT exist pre-EDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_or_post_eds(self, home_and_eds: HomeAndEds) -> str:
        """
        Validates the object using either pre- or post- EDS.
        :return: Error message iff validation failed.
        """
        error_message = self.validate_pre_eds_if_applicable(home_and_eds.home_dir_path)
        if error_message is not None:
            return error_message
        return self.validate_post_eds_if_applicable(home_and_eds.eds)


class ConstantSuccessValidator(PreOrPostEdsValidator):
    def validate_pre_eds_if_applicable(self, home_dir_path: pathlib.Path) -> str:
        return None

    def validate_post_eds_if_applicable(self, eds: ExecutionDirectoryStructure) -> str:
        return None


class AndValidator(PreOrPostEdsValidator):
    def __init__(self,
                 validators: iter):
        self.validators = validators

    def validate_pre_eds_if_applicable(self, home_dir_path: pathlib.Path) -> str:
        for validator in self.validators:
            result = validator.validate_pre_eds_if_applicable(home_dir_path)
            if result is not None:
                return result
        return None

    def validate_post_eds_if_applicable(self, eds: ExecutionDirectoryStructure) -> str:
        for validator in self.validators:
            result = validator.validate_post_eds_if_applicable(eds)
            if result is not None:
                return result
        return None


class PreOrPostEdsSvhValidationErrorValidator:
    """
    A validator that translates error messages to a svh.ValidationError
    """

    def __init__(self,
                 validator: PreOrPostEdsValidator):
        self.validator = validator

    def validate_pre_eds_if_applicable(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        return self._translate(self.validator.validate_pre_eds_if_applicable(home_dir_path))

    def validate_post_eds_if_applicable(self,
                                        eds: ExecutionDirectoryStructure) -> svh.SuccessOrValidationErrorOrHardError:
        return self._translate(self.validator.validate_post_eds_if_applicable(eds))

    def validate_pre_or_post_eds(self, home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
        return self._translate(self.validator.validate_pre_or_post_eds(home_and_eds))

    @staticmethod
    def _translate(error_message_or_none: str) -> svh.SuccessOrValidationErrorOrHardError:
        if error_message_or_none is not None:
            return svh.new_svh_validation_error(error_message_or_none)
        return svh.new_svh_success()


class PreOrPostEdsSvhValidationForSuccessOrHardError:
    """
    A validator that translates error messages to a sh.HardError
    """

    def __init__(self,
                 validator: PreOrPostEdsValidator):
        self.validator = validator

    def validate_pre_eds_if_applicable(self, home_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return self._translate(self.validator.validate_pre_eds_if_applicable(home_dir_path))

    def validate_post_eds_if_applicable(self, eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
        return self._translate(self.validator.validate_post_eds_if_applicable(eds))

    def validate_pre_or_post_eds(self, home_and_eds: HomeAndEds) -> sh.SuccessOrHardError:
        return self._translate(self.validator.validate_pre_or_post_eds(home_and_eds))

    @staticmethod
    def _translate(error_message_or_none: str) -> sh.SuccessOrHardError:
        if error_message_or_none is not None:
            return sh.new_sh_hard_error(error_message_or_none)
        return sh.new_sh_success()
