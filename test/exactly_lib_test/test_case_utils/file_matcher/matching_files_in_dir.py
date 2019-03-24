import pathlib
import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib_test.test_case_utils.file_matcher.test_resources.file_matchers import ConstantResultMatcher
from exactly_lib_test.test_case_utils.file_matcher.test_resources.single_dir_checks import single_dir_setup
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, empty_dir


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestMatchingFilesInDir)


class TestMatchingFilesInDir(unittest.TestCase):
    file_1_name = 'file 1 name'
    dir_2_name = 'dir 2 name'
    file_3_name = 'file 3 name'

    def _check(self,
               matcher: sut.FileMatcher,
               expected_matching_file_base_names: set):
        dir_contents = DirContents([
            empty_file(self.file_1_name),
            empty_dir(self.dir_2_name),
            empty_file(self.file_3_name),
        ])
        with single_dir_setup(dir_contents) as setup:
            # ACT #
            actual_matching_file_paths = sut.matching_files_in_dir(matcher,
                                                                   setup.model_with_action_dir_as_path_to_match())
            # ASSERT #
            actual_matching_file_base_names = set(map(pathlib.Path.name.fget, actual_matching_file_paths))
            self.assertEqual(expected_matching_file_base_names,
                             actual_matching_file_base_names)

    def test_match_every_file(self):
        self._check(ConstantResultMatcher(True),
                    {self.file_1_name,
                     self.dir_2_name,
                     self.file_3_name})

    def test_match_no_file(self):
        self._check(ConstantResultMatcher(False),
                    set())

    def test_match_some_files(self):
        self._check(BaseNameMatcher(self.file_1_name),
                    {self.file_1_name})


class BaseNameMatcher(sut.FileMatcher):
    def __init__(self, base_name_that_matches: str):
        self.base_name_that_matches = base_name_that_matches

    def matches(self, model: FileMatcherModel) -> bool:
        return model.path.name == self.base_name_that_matches

    @property
    def option_description(self) -> str:
        return 'option description'
