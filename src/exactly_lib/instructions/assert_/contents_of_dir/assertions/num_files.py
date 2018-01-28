import pathlib
from typing import Sequence

from exactly_lib.instructions.assert_.contents_of_dir import config
from exactly_lib.instructions.assert_.contents_of_dir.assertions import common
from exactly_lib.instructions.assert_.contents_of_dir.assertions.common import DirContentsAssertionPart
from exactly_lib.instructions.utils.validators import PreOrPostSdsValidatorFromValidatorViaExceptions, \
    SvhValidatorViaExceptionsFromPreAndPostSdsValidators
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.condition import comparison_structures
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as parse_expr
from exactly_lib.type_system.logic import file_matcher as file_matcher_type


class NumFilesResolver(comparison_structures.OperandResolver):
    def __init__(self,
                 path_to_check: FileRefResolver,
                 file_matcher: FileMatcherResolver):
        super().__init__(config.NUM_FILES_PROPERTY_NAME)
        self.path_to_check = path_to_check
        self.file_matcher = file_matcher

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
                             SvhValidatorViaExceptionsFromPreAndPostSdsValidators(
                                 pre_sds=self._comparison_handler.validator)))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._comparison_handler.references + self._settings.file_matcher.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              settings: common.Settings) -> common.Settings:
        self._comparison_handler.execute(environment)
        return self._settings
