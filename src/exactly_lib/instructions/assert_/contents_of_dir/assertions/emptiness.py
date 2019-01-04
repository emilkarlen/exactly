import pathlib
from typing import Sequence, List, Optional

from exactly_lib.instructions.assert_.contents_of_dir import config
from exactly_lib.instructions.assert_.contents_of_dir.assertions import common
from exactly_lib.instructions.assert_.contents_of_dir.assertions.common import FilesSource, \
    FilesMatcherResolverBase
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.error_messages import path_resolving_env_from_err_msg_env
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.file_or_dir_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, PropertyDescriptor, \
    ErrorMessageResolver
from exactly_lib.type_system.logic import file_matcher as file_matcher_type
from exactly_lib.util.logic_types import ExpectationType


class EmptinessAssertion(FilesMatcherResolverBase):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._settings.file_matcher.references

    def matches(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                files_source: FilesSource) -> Optional[ErrorMessageResolver]:
        err_msg_setup = _ErrMsgSetup(files_source.path_of_dir,
                                     self._settings.property_descriptor(config.EMPTINESS_PROPERTY_NAME,
                                                                        files_source.path_of_dir),
                                     self._settings.expectation_type,
                                     EMPTINESS_CHECK_EXPECTED_VALUE)
        executor = _EmptinessExecutor(
            err_msg_setup,
            environment,
            self._settings,
            files_source)

        return executor.main()


class _ErrMsgSetup:
    def __init__(self,
                 root_dir_path_resolver: FileRefResolver,
                 property_descriptor: PropertyDescriptor,
                 expectation_type: ExpectationType,
                 expected_description_str: str,
                 ):
        self.expectation_type = expectation_type
        self.property_descriptor = property_descriptor
        self.root_dir_path_resolver = root_dir_path_resolver
        self.expected_description_str = expected_description_str


class _EmptinessExecutor:
    def __init__(self,
                 err_msg_setup: _ErrMsgSetup,
                 environment: InstructionEnvironmentForPostSdsStep,
                 settings: common.Settings,
                 files_source: FilesSource):
        self.err_msg_setup = err_msg_setup
        self.path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        self.settings = settings
        self.files_source = files_source
        self.error_message_setup = err_msg_setup

    def main(self) -> Optional[ErrorMessageResolver]:
        files_in_dir = self._files_in_dir_to_check()

        if self.settings.expectation_type is ExpectationType.POSITIVE:
            return self._fail_if_path_dir_is_not_empty(files_in_dir)
        else:
            return self._fail_if_path_dir_is_empty(files_in_dir)

    def _files_in_dir_to_check(self) -> list:
        dir_path_to_check = self.files_source.path_of_dir.resolve_value_of_any_dependency(self.path_resolving_env)
        assert isinstance(dir_path_to_check, pathlib.Path), 'Resolved value should be a path'
        file_matcher = self.settings.file_matcher.resolve(self.path_resolving_env.symbols)
        selected_files = file_matcher_type.matching_files_in_dir(file_matcher, dir_path_to_check)
        return list(selected_files)

    def _fail_if_path_dir_is_not_empty(self, files_in_dir: list) -> Optional[ErrorMessageResolver]:
        num_files_in_dir = len(files_in_dir)
        if num_files_in_dir != 0:
            return _ErrorMessageResolver(self.err_msg_setup, files_in_dir)

    def _fail_if_path_dir_is_empty(self, files_in_dir: list) -> Optional[ErrorMessageResolver]:
        num_files_in_dir = len(files_in_dir)
        if num_files_in_dir == 0:
            return _ErrorMessageResolver(self.err_msg_setup, files_in_dir)


class _ErrorMessageResolver(ErrorMessageResolver):
    def __init__(self,
                 setup: _ErrMsgSetup,
                 actual_files: List[pathlib.Path],
                 ):
        self._setup = setup
        self._actual_files = actual_files

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        return self.resolve_diff(environment).error_message()

    def resolve_diff(self,
                     environment: ErrorMessageResolvingEnvironment) -> diff_msg.DiffErrorInfo:
        return diff_msg.DiffErrorInfo(
            self._setup.property_descriptor.description(environment),
            self._setup.expectation_type,
            self._setup.expected_description_str,
            self.resolve_actual_info(self._actual_files,
                                     path_resolving_env_from_err_msg_env(environment))
        )

    def resolve_actual_info(self,
                            actual_files: List[pathlib.Path],
                            environment: PathResolvingEnvironmentPreOrPostSds) -> diff_msg.ActualInfo:
        num_files_in_dir = len(actual_files)
        single_line_value = str(num_files_in_dir) + ' files'
        return diff_msg.ActualInfo(single_line_value,
                                   self._resolve_description_lines(actual_files, environment))

    def _resolve_description_lines(self,
                                   actual_files: List[pathlib.Path],
                                   environment: PathResolvingEnvironmentPreOrPostSds) -> List[str]:
        return ['Actual contents:'] + self._dir_contents_err_msg_lines(actual_files, environment)

    def _dir_contents_err_msg_lines(self,
                                    actual_files_in_dir: List[pathlib.Path],
                                    environment: PathResolvingEnvironmentPreOrPostSds) -> List[str]:
        root_dir_path = self._setup.root_dir_path_resolver.resolve_value_of_any_dependency(environment)
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
