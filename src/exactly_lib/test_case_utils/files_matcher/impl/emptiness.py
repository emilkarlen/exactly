from typing import Sequence, List, Optional, Iterator

from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.file_or_dir_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.files_matcher.impl import files_matchers
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.files_matcher import FileModel, FilesMatcherModel, FilesMatcher, \
    FilesMatcherConstructor, FilesMatcherDdv
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util import logic_types, strings
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def emptiness_matcher() -> FilesMatcherSdv:
    return _EmptinessMatcherSdv()


class _EmptinessMatcherSdv(FilesMatcherSdv):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        return _EmptinessMatcherDdv()


class _EmptinessMatcherDdv(FilesMatcherDdv):
    def value_of_any_dependency(self, tcds: Tcds) -> FilesMatcherConstructor:
        return files_matchers.ConstantConstructor(
            _EmptinessMatcher(ExpectationType.POSITIVE)
        )


class _EmptinessMatcher(FilesMatcher):
    def __init__(self, expectation_type: ExpectationType):
        self._expectation_type = expectation_type

    @property
    def name(self) -> str:
        return file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

    @property
    def negation(self) -> FilesMatcher:
        return _EmptinessMatcher(logic_types.negation(self._expectation_type))

    def matches_emr(self, files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        err_msg_setup = _ErrMsgSetup(files_source,
                                     self._expectation_type,
                                     EMPTINESS_CHECK_EXPECTED_VALUE)
        executor = _EmptinessExecutor(
            err_msg_setup,
            self._expectation_type,
            files_source)

        return executor.main()

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        files_list = list(model.files())
        num_files_in_dir = len(files_list)
        if num_files_in_dir != 0:
            return MatchingResult(
                False,
                _FailureTraceRenderer(
                    self.name,
                    files_list,
                    model,
                )
            )
        else:
            return self._new_tb().build_result(True)


class _ErrMsgSetup:
    def __init__(self,
                 model: FilesMatcherModel,
                 expectation_type: ExpectationType,
                 expected_description_str: str,
                 ):
        self.expectation_type = expectation_type
        self.model = model
        self.expected_description_str = expected_description_str


class _FailureTraceRenderer(NodeRenderer[bool]):
    def __init__(self,
                 matcher_name: str,
                 actual_contents: List[FileModel],
                 model: FilesMatcherModel):
        self._matcher_name = matcher_name
        self._actual_contents = actual_contents
        self._model = model

    def render(self) -> Node[bool]:
        return Node(
            self._matcher_name,
            False,
            self._details(),
            ()
        )

    def _details(self) -> Sequence[tree.Detail]:
        renderer = details.HeaderAndValue(
            strings.FormatPositional(
                'Actual contents ({} files)', len(self._actual_contents),
            ),
            custom_details.StringList(self._dir_contents_err_msg_lines()),

        )
        return renderer.render()

    def _dir_contents_err_msg_lines(self) -> List[str]:
        paths_in_dir = [
            f.relative_to_root_dir
            for f in self._actual_contents
        ]
        if len(paths_in_dir) < 50:
            paths_in_dir.sort()
        num_files_to_display = 5
        ret_val = [
            str(p)
            for p in paths_in_dir[:num_files_to_display]
        ]
        if len(self._actual_contents) > num_files_to_display:
            ret_val.append('...')
        return ret_val


class _EmptinessExecutor:
    def __init__(self,
                 err_msg_setup: _ErrMsgSetup,
                 expectation_type: ExpectationType,
                 model: FilesMatcherModel):
        self.err_msg_setup = err_msg_setup
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

    def resolve(self) -> str:
        return self.resolve_diff().error_message()

    def resolve_diff(self) -> diff_msg.DiffErrorInfo:
        property_descriptor = self._setup.model.error_message_info.property_descriptor
        return diff_msg.DiffErrorInfo(
            property_descriptor(config.EMPTINESS_PROPERTY_NAME).description(),
            self._setup.expectation_type,
            self._setup.expected_description_str,
            self.resolve_actual_info(self._actual_files)
        )

    def resolve_actual_info(self, actual_files: List[FileModel]) -> diff_msg.ActualInfo:
        num_files_in_dir = len(actual_files)
        single_line_value = str(num_files_in_dir) + ' files'
        return diff_msg.ActualInfo(single_line_value,
                                   self._resolve_description_lines(actual_files))

    def _resolve_description_lines(self, actual_files: List[FileModel]) -> List[str]:
        return ['Actual contents:'] + self._dir_contents_err_msg_lines(actual_files)

    def _dir_contents_err_msg_lines(self, actual_files_in_dir: List[FileModel]) -> List[str]:
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


_INDENT = '  '
