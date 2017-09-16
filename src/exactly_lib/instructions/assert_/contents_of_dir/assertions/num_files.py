import pathlib

from exactly_lib.instructions.assert_.contents_of_dir import config
from exactly_lib.instructions.assert_.contents_of_dir.assertions import common
from exactly_lib.instructions.assert_.contents_of_dir.assertions.common import DirContentsAssertionPart
from exactly_lib.instructions.assert_.utils.expression import comparison_structures
from exactly_lib.instructions.assert_.utils.expression import parse as parse_expr
from exactly_lib.instructions.utils.validators import SvhValidatorViaExceptions, SvhPreSdsValidatorViaExceptions, \
    PreOrPostSdsValidatorFromValidatorViaExceptions
from exactly_lib.named_element.path_resolving_environment import PathResolvingEnvironmentPreSds
from exactly_lib.named_element.resolver_structure import FileMatcherResolver
from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.type_system.logic import file_matcher as file_matcher_type


class InstructionForNumFiles(common._InstructionBase):
    def __init__(self,
                 settings: common.Settings,
                 operator_and_r_operand: parse_expr.IntegerComparisonOperatorAndRightOperand):
        super().__init__(settings)
        self._assertion_part = NumFilesAssertion(settings, operator_and_r_operand)

    def symbol_usages(self) -> list:
        return self._assertion_part.references

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        err_msg = self._assertion_part.validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)
        if err_msg:
            return svh.new_svh_validation_error(err_msg)
        else:
            return svh.new_svh_success()

    def _main_after_checking_existence_of_dir(self,
                                              environment: InstructionEnvironmentForPostSdsStep,
                                              os_services: OsServices):
        self._assertion_part.check(environment, os_services, self.settings)


class NumFilesResolver(comparison_structures.OperandResolver):
    def __init__(self,
                 path_to_check: FileRefResolver,
                 file_matcher: FileMatcherResolver):
        super().__init__(config.NUM_FILES_PROPERTY_NAME)
        self.path_to_check = path_to_check
        self.file_matcher = file_matcher

    @property
    def references(self) -> list:
        return self.path_to_check.references

    def resolve(self, environment: InstructionEnvironmentForPostSdsStep) -> int:
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        path_to_check = self.path_to_check.resolve_value_of_any_dependency(path_resolving_env)
        assert isinstance(path_to_check, pathlib.Path), 'Resolved value should be a path'
        file_matcher = self.file_matcher.resolve(environment.symbols)
        selected_files = file_matcher_type.matching_files_in_dir(file_matcher, path_to_check)
        return len(list(selected_files))


class NumFilesAssertion(DirContentsAssertionPart):
    def __init__(self,
                 settings: common.Settings,
                 operator_and_r_operand: parse_expr.IntegerComparisonOperatorAndRightOperand):
        self._comparison_handler = comparison_structures.ComparisonHandler(
            settings.property_descriptor(config.NUM_FILES_PROPERTY_NAME),
            settings.expectation_type,
            NumFilesResolver(settings.path_to_check,
                             settings.file_matcher),
            operator_and_r_operand.operator,
            operator_and_r_operand.right_operand)
        super().__init__(settings,
                         PreOrPostSdsValidatorFromValidatorViaExceptions(
                             _Validator(self._comparison_handler.validator)))

    @property
    def references(self) -> list:
        return self._comparison_handler.references + self._settings.file_matcher.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              settings: common.Settings) -> common.Settings:
        self._comparison_handler.execute(environment)
        return self._settings


class _Validator(SvhValidatorViaExceptions):
    def __init__(self, validator: SvhPreSdsValidatorViaExceptions):
        self.validator = validator

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        self.validator.validate_pre_sds(environment)
