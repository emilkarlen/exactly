from typing import Sequence, List, Optional, Iterator

from exactly_lib.symbol.error_messages import path_resolving_env_from_err_msg_env
from exactly_lib.symbol.files_matcher import FilesMatcherResolver, \
    Environment, FileModel, FilesMatcherModel, FilesMatcherValue
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.file_or_dir_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.files_matcher.files_matchers import FilesMatcherResolverBase
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, ErrorMessageResolver
from exactly_lib.util import logic_types
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def emptiness_matcher(expectation_type: ExpectationType) -> FilesMatcherResolver:
    return _EmptinessMatcher(expectation_type)


class _EmptinessMatcher(FilesMatcherResolverBase):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    @property
    def negation(self) -> FilesMatcherResolver:
        return _EmptinessMatcher(logic_types.negation(self._expectation_type),
                                 self._validator)

    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        return _EmptinessMatcherValue(self._expectation_type)


class _EmptinessMatcherValue(FilesMatcherValue):
    def __init__(self, expectation_type: ExpectationType):
        self._expectation_type = expectation_type

    @property
    def negation(self) -> FilesMatcherValue:
        return _EmptinessMatcherValue(logic_types.negation(self._expectation_type))

    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        err_msg_setup = _ErrMsgSetup(files_source,
                                     self._expectation_type,
                                     EMPTINESS_CHECK_EXPECTED_VALUE)
        executor = _EmptinessExecutor(
            err_msg_setup,
            environment,
            self._expectation_type,
            files_source)

        return executor.main()


class _ErrMsgSetup:
    def __init__(self,
                 model: FilesMatcherModel,
                 expectation_type: ExpectationType,
                 expected_description_str: str,
                 ):
        self.expectation_type = expectation_type
        self.model = model
        self.expected_description_str = expected_description_str


class _EmptinessExecutor:
    def __init__(self,
                 err_msg_setup: _ErrMsgSetup,
                 environment: Environment,
                 expectation_type: ExpectationType,
                 model: FilesMatcherModel):
        self.err_msg_setup = err_msg_setup
        self.path_resolving_env = environment.path_resolving_environment
        self.expectation_type = expectation_type
        self.error_message_setup = err_msg_setup
        self.model = model

    def main(self) -> Optional[ErrorMessageResolver]:
        files_in_dir = self.model.files()

        if self.expectation_type is ExpectationType.POSITIVE:
            return self._fail_if_path_dir_is_not_empty(files_in_dir)
        else:
            return self._fail_if_path_dir_is_empty(files_in_dir)

    def _fail_if_path_dir_is_not_empty(self, files_in_dir: Iterator[FileModel]) -> Optional[ErrorMessageResolver]:
        files_list = list(files_in_dir)
        num_files_in_dir = len(files_list)
        if num_files_in_dir != 0:
            return _ErrorMessageResolver(self.err_msg_setup, files_list)

    def _fail_if_path_dir_is_empty(self, files_in_dir: Iterator[FileModel]) -> Optional[ErrorMessageResolver]:
        files_list = list(files_in_dir)
        num_files_in_dir = len(files_list)
        if num_files_in_dir == 0:
            return _ErrorMessageResolver(self.err_msg_setup, files_list)


class _ErrorMessageResolver(ErrorMessageResolver):
    def __init__(self,
                 setup: _ErrMsgSetup,
                 actual_files: List[FileModel],
                 ):
        self._setup = setup
        self._actual_files = actual_files

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        return self.resolve_diff(environment).error_message()

    def resolve_diff(self,
                     environment: ErrorMessageResolvingEnvironment) -> diff_msg.DiffErrorInfo:
        property_descriptor = self._setup.model.error_message_info.property_descriptor
        return diff_msg.DiffErrorInfo(
            property_descriptor(config.EMPTINESS_PROPERTY_NAME).description(environment),
            self._setup.expectation_type,
            self._setup.expected_description_str,
            self.resolve_actual_info(self._actual_files,
                                     path_resolving_env_from_err_msg_env(environment))
        )

    def resolve_actual_info(self,
                            actual_files: List[FileModel],
                            environment: PathResolvingEnvironmentPreOrPostSds) -> diff_msg.ActualInfo:
        num_files_in_dir = len(actual_files)
        single_line_value = str(num_files_in_dir) + ' files'
        return diff_msg.ActualInfo(single_line_value,
                                   self._resolve_description_lines(actual_files, environment))

    def _resolve_description_lines(self,
                                   actual_files: List[FileModel],
                                   environment: PathResolvingEnvironmentPreOrPostSds) -> List[str]:
        return ['Actual contents:'] + self._dir_contents_err_msg_lines(actual_files, environment)

    def _dir_contents_err_msg_lines(self,
                                    actual_files_in_dir: List[FileModel],
                                    environment: PathResolvingEnvironmentPreOrPostSds) -> List[str]:
        paths_in_dir = [
            f.relative_to_root_dir
            for f in actual_files_in_dir
        ]
        if len(paths_in_dir) < 50:
            paths_in_dir.sort()
        num_files_to_display = 5
        ret_val = [
            str(p)
            for p in paths_in_dir[:num_files_to_display]
        ]
        if len(actual_files_in_dir) > num_files_to_display:
            ret_val.append('...')
        return ret_val
