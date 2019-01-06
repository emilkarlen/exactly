from typing import Sequence, Optional

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.condition import comparison_structures
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as parse_expr
from exactly_lib.test_case_utils.files_matcher import files_matchers, config
from exactly_lib.test_case_utils.files_matcher.files_matchers import FilesMatcherResolverBaseForNewModel
from exactly_lib.test_case_utils.files_matcher.new_model import FilesMatcherModel
from exactly_lib.test_case_utils.files_matcher.structure import FilesMatcherResolver, \
    Environment
from exactly_lib.test_case_utils.validators import PreOrPostSdsValidatorFromValidatorViaExceptions, \
    SvhValidatorViaExceptionsFromPreAndPostSdsValidators
from exactly_lib.type_system.error_message import ErrorMessageResolver


def num_files_matcher(settings: files_matchers.Settings,
                      operator_and_r_operand: parse_expr.IntegerComparisonOperatorAndRightOperand
                      ) -> FilesMatcherResolver:
    return _NumFilesMatcher(settings, operator_and_r_operand)


class _NumFilesMatcher(FilesMatcherResolverBaseForNewModel):
    def __init__(self,
                 settings: files_matchers.Settings,
                 operator_and_r_operand: parse_expr.IntegerComparisonOperatorAndRightOperand):
        self._settings = settings
        self._operator_and_r_operand = operator_and_r_operand
        self._references = self._operator_and_r_operand.right_operand.references

        validator = PreOrPostSdsValidatorFromValidatorViaExceptions(
            SvhValidatorViaExceptionsFromPreAndPostSdsValidators(
                pre_sds=comparison_structures.OperandValidator(operator_and_r_operand.right_operand))
        )
        super().__init__(settings,
                         validator)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._operator_and_r_operand.right_operand.references

    def matches_new(self,
                    environment: Environment,
                    files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        comparison_handler = comparison_structures.ComparisonHandler(
            files_source.error_message_info.property_descriptor(config.NUM_FILES_PROPERTY_NAME),
            self._settings.expectation_type,
            NumFilesResolver(files_source,
                             self._settings.file_matcher),
            self._operator_and_r_operand.operator,
            self._operator_and_r_operand.right_operand)

        env = environment.path_resolving_environment

        return comparison_handler.execute_and_report_as_err_msg_resolver(env)


class NumFilesResolver(comparison_structures.OperandResolver[int]):
    def __init__(self,
                 path_to_check: FilesMatcherModel,
                 file_matcher: FileMatcherResolver):
        super().__init__(config.NUM_FILES_PROPERTY_NAME)
        self.path_to_check = path_to_check
        self.file_matcher = file_matcher

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> int:
        return len(list(self.path_to_check.files()))
