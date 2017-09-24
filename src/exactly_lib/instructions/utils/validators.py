from exactly_lib.instructions.utils import return_svh_via_exceptions
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreSds
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator


class SvhValidatorViaReturnValues:
    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self, environment: PathResolvingEnvironmentPostSds
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class SvhPreSdsValidatorViaExceptions:
    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        """
        :raises SvhException: Validation fails
        """
        pass


class SvhPostSetupValidatorViaExceptions:
    def validate_post_setup(self, environment: PathResolvingEnvironmentPostSds):
        """
        :raises SvhException: Validation fails
        """
        pass


class SvhValidatorViaExceptions(SvhPreSdsValidatorViaExceptions,
                                SvhPostSetupValidatorViaExceptions):
    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        """
        :raises SvhException: Validation fails
        """
        pass

    def validate_post_setup(self, environment: PathResolvingEnvironmentPostSds):
        """
        :raises SvhException: Validation fails
        """
        pass


class SvhValidatorViaExceptionsFromPreAndPostSdsValidators(SvhValidatorViaExceptions):
    def __init__(self,
                 pre_sds: SvhPreSdsValidatorViaExceptions = None,
                 post_setup: SvhPostSetupValidatorViaExceptions = None,
                 ):
        self._pre_sds = pre_sds
        self._post_setup = post_setup

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        if self._pre_sds:
            self._pre_sds.validate_pre_sds(environment)

    def validate_post_setup(self, environment: PathResolvingEnvironmentPostSds):
        if self._post_setup:
            self._post_setup.validate_post_setup(environment)


class PreOrPostSdsValidatorFromValidatorViaExceptions(PreOrPostSdsValidator):
    def __init__(self, adapted: SvhValidatorViaExceptions):
        self._adapted = adapted

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> str:
        try:
            self._adapted.validate_pre_sds(environment)
        except return_svh_via_exceptions.SvhException as ex:
            return ex.err_msg

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> str:
        try:
            self._adapted.validate_post_setup(environment)
        except return_svh_via_exceptions.SvhException as ex:
            return ex.err_msg


class SvhValidatorViaReturnValuesFromValidatorViaExceptions(SvhValidatorViaReturnValues):
    def __init__(self, adapted: SvhValidatorViaExceptions):
        self._adapted = adapted

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> svh.SuccessOrValidationErrorOrHardError:
        return return_svh_via_exceptions.translate_svh_exception_to_svh(self._adapted.validate_pre_sds, environment)

    def validate_post_setup(self,
                            environment: PathResolvingEnvironmentPostSds) -> svh.SuccessOrValidationErrorOrHardError:
        return return_svh_via_exceptions.translate_svh_exception_to_svh(self._adapted.validate_post_setup, environment)
