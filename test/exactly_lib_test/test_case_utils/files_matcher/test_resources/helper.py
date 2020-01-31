from typing import Optional

from exactly_lib_test.test_case_utils.files_matcher.test_resources import model
from exactly_lib_test.test_case_utils.files_matcher.test_resources.model import ModelConstructor
from exactly_lib_test.test_case_utils.test_resources.file_files_matcher import IntegrationCheckWFilesMatcherHelperBase


class IntegrationCheckHelper(IntegrationCheckWFilesMatcherHelperBase):
    def model_constructor_for_checked_dir__recursive(self,
                                                     min_depth: Optional[int] = None,
                                                     max_depth: Optional[int] = None,
                                                     ) -> ModelConstructor:
        return model.model_constructor__recursive(self.dir_arg.path_sdv,
                                                  min_depth,
                                                  max_depth)
