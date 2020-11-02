from typing import List, Optional

from exactly_lib_test.impls.types.file_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.file_matcher.test_resources.integration_check import ModelConstructor
from exactly_lib_test.impls.types.files_matcher.models.test_resources.test_data import FileElementForTest
from exactly_lib_test.impls.types.test_resources.file_files_matcher import IntegrationCheckWFilesMatcherHelperBase
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement
from exactly_lib_test.test_resources.strings import WithToString
from exactly_lib_test.test_resources.test_utils import EA


class DepthArgs:
    def __init__(self,
                 min_depth: Optional[WithToString] = None,
                 max_depth: Optional[WithToString] = None,
                 ):
        self.max_depth = max_depth
        self.min_depth = min_depth

    def min_depth_arg(self):
        raise NotImplementedError('todo')


class LimitationCase:
    def __init__(self,
                 depth_args: DepthArgs,
                 data: EA[List[FileElementForTest], List[FileSystemElement]]
                 ):
        self.depth_args = depth_args
        self.data = data


class IntegrationCheckHelper(IntegrationCheckWFilesMatcherHelperBase):
    def model_constructor_for_checked_dir(self) -> ModelConstructor:
        return integration_check.file_in_tcds(self.dir_arg.location,
                                              self.dir_arg.name)
