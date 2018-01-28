import pathlib
from typing import Sequence

from exactly_lib.instructions.assert_.contents_of_dir import config
from exactly_lib.instructions.assert_.contents_of_dir.assertions import common
from exactly_lib.instructions.assert_.contents_of_dir.assertions.common import Settings, \
    DirContentsAssertionPart
from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions as pfh_ex_method
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import property_description, diff_msg
from exactly_lib.type_system.logic import file_matcher as file_matcher_type
from exactly_lib.util.logic_types import ExpectationType


class _ErrorMessageResolver:
    def __init__(self,
                 root_dir_path_resolver: FileRefResolver,
                 property_descriptor: property_description.PropertyDescriptor,
                 expectation_type: ExpectationType,
                 expected_description_str: str,
                 ):
        self.expectation_type = expectation_type
        self.property_descriptor = property_descriptor
        self.root_dir_path_resolver = root_dir_path_resolver
        self.expected_description_str = expected_description_str

    def resolve(self,
                actual_files: list,
                environment: InstructionEnvironmentForPostSdsStep) -> diff_msg.DiffErrorInfo:
        return diff_msg.DiffErrorInfo(
            self.property_descriptor.description(environment),
            self.expectation_type,
            self.expected_description_str,
            self.resolve_actual_info(actual_files, environment.path_resolving_environment_pre_or_post_sds))

    def resolve_actual_info(self, actual_files: list,
                            environment: PathResolvingEnvironmentPreOrPostSds) -> diff_msg.ActualInfo:
        num_files_in_dir = len(actual_files)
        single_line_value = str(num_files_in_dir) + ' files'
        return diff_msg.ActualInfo(single_line_value,
                                   self._resolve_description_lines(actual_files, environment))

    def _resolve_description_lines(self,
                                   actual_files: list,
                                   environment: PathResolvingEnvironmentPreOrPostSds) -> list:
        return ['Actual contents:'] + self._dir_contents_err_msg_lines(actual_files, environment)

    def _dir_contents_err_msg_lines(self,
                                    actual_files_in_dir: list,
                                    environment: PathResolvingEnvironmentPreOrPostSds) -> list:
        root_dir_path = self.root_dir_path_resolver.resolve_value_of_any_dependency(environment)
        if len(actual_files_in_dir) < 50:
            actual_files_in_dir.sort()
        num_files_to_display = 5
        ret_val = [
            str(p.relative_to(root_dir_path))
            for p in actual_files_in_dir[:num_files_to_display]
        ]
        if len(actual_files_in_dir) > num_files_to_display:
            ret_val.append('...')
        return ret_val


class _EmptinessChecker:
    def __init__(self,
                 property_descriptor: property_description.PropertyDescriptor,
                 environment: InstructionEnvironmentForPostSdsStep,
                 settings: common.Settings):
        self.property_descriptor = property_descriptor
        self.environment = environment
        self.path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        self.settings = settings
        self.error_message_resolver = _ErrorMessageResolver(settings.path_to_check,
                                                            property_descriptor,
                                                            settings.expectation_type,
                                                            EMPTINESS_CHECK_EXPECTED_VALUE)

    def main(self):
        files_in_dir = self._files_in_dir_to_check()

        if self.settings.expectation_type is ExpectationType.POSITIVE:
            self._fail_if_path_dir_is_not_empty(files_in_dir)
        else:
            self._fail_if_path_dir_is_empty(files_in_dir)

    def _files_in_dir_to_check(self) -> list:
        dir_path_to_check = self.settings.path_to_check.resolve_value_of_any_dependency(self.path_resolving_env)
        assert isinstance(dir_path_to_check, pathlib.Path), 'Resolved value should be a path'
        file_matcher = self.settings.file_matcher.resolve(self.path_resolving_env.symbols)
        selected_files = file_matcher_type.matching_files_in_dir(file_matcher, dir_path_to_check)
        return list(selected_files)

    def _fail_if_path_dir_is_not_empty(self, files_in_dir: list):
        num_files_in_dir = len(files_in_dir)
        if num_files_in_dir != 0:
            self._fail_with_err_msg(files_in_dir)

    def _fail_if_path_dir_is_empty(self, files_in_dir: list):
        num_files_in_dir = len(files_in_dir)
        if num_files_in_dir == 0:
            self._fail_with_err_msg(files_in_dir)

    def _fail_with_err_msg(self,
                           files_in_dir: list):
        diff_failure_info = self.error_message_resolver.resolve(files_in_dir, self.environment)
        msg = diff_failure_info.error_message()
        raise pfh_ex_method.PfhFailException(msg)


class EmptinessAssertion(DirContentsAssertionPart):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._settings.file_matcher.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              settings: Settings) -> Settings:
        checker = _EmptinessChecker(self._settings.property_descriptor(config.EMPTINESS_PROPERTY_NAME),
                                    environment,
                                    self._settings)
        checker.main()
        return self._settings
