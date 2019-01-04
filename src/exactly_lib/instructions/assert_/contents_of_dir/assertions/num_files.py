import pathlib
from typing import Sequence

from exactly_lib.instructions.assert_.contents_of_dir import config, files_matchers
from exactly_lib.instructions.assert_.contents_of_dir.assertions.common import DirContentsAssertionPart
from exactly_lib.instructions.assert_.contents_of_dir.files_matcher import FilesSource
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.condition import comparison_structures
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as parse_expr
from exactly_lib.test_case_utils.validators import PreOrPostSdsValidatorFromValidatorViaExceptions, \
    SvhValidatorViaExceptionsFromPreAndPostSdsValidators
from exactly_lib.type_system.logic import file_matcher as file_matcher_type


class NumFilesResolver(comparison_structures.OperandResolver[int]):
    def __init__(self,
                 path_to_check: FileRefResolver,
                 file_matcher: FileMatcherResolver):
        super().__init__(config.NUM_FILES_PROPERTY_NAME)
        self.path_to_check = path_to_check
        self.file_matcher = file_matcher

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> int:
        path_to_check = self.path_to_check.resolve_value_of_any_dependency(environment)
        assert isinstance(path_to_check, pathlib.Path), 'Resolved value should be a path'
        file_matcher = self.file_matcher.resolve(environment.symbols)
        selected_files = file_matcher_type.matching_files_in_dir(file_matcher, path_to_check)
        return len(list(selected_files))


class NumFilesAssertion(DirContentsAssertionPart):
    def __init__(self,
                 settings: files_matchers.Settings,
                 operator_and_r_operand: parse_expr.IntegerComparisonOperatorAndRightOperand):
        self._settings = settings
        self._operator_and_r_operand = operator_and_r_operand
        self._references = references_from_objects_with_symbol_references([
            self._operator_and_r_operand.right_operand,
            self._settings.file_matcher
        ])

        validator = PreOrPostSdsValidatorFromValidatorViaExceptions(
            SvhValidatorViaExceptionsFromPreAndPostSdsValidators(
                pre_sds=comparison_structures.OperandValidator(operator_and_r_operand.right_operand))
        )
        super().__init__(settings,
                         validator)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              files_source: FilesSource) -> FilesSource:
        comparison_handler = comparison_structures.ComparisonHandler(
            self._settings.property_descriptor(config.NUM_FILES_PROPERTY_NAME,
                                               files_source.path_of_dir),
            self._settings.expectation_type,
            NumFilesResolver(files_source.path_of_dir,
                             self._settings.file_matcher),
            self._operator_and_r_operand.operator,
            self._operator_and_r_operand.right_operand)

        comparison_handler.execute(environment.path_resolving_environment_pre_or_post_sds)

        return files_source
