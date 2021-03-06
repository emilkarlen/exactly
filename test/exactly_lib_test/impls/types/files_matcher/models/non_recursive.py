import unittest

from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.files_matcher import models as sut
from exactly_lib.type_val_deps.types.path.path_ddv import DescribedPath
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.file_matcher.test_resources.file_matchers import FileMatcherTestImplBase
from exactly_lib_test.impls.types.files_matcher.models.test_resources import test_data
from exactly_lib_test.impls.types.files_matcher.models.test_resources.checker import check
from exactly_lib_test.test_resources.files.file_structure import Dir, File
from exactly_lib_test.type_val_prims.matcher.test_resources import matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCase),
    ])


class TestCase(unittest.TestCase):
    def test_WHEN_no_selector_THEN_all_files_SHOULD_be_in_model(self):
        # ARRANGE #

        cases = test_data.strip_file_type_info_s(
            [
                test_data.expected_is_direct_contents_of_actual(case.name, case.value)
                for case in test_data.cases()
            ]
        )

        # ACT & ASSERT #

        check(self,
              sut.non_recursive,
              cases)

    def test_WHEN_single_selector_THEN_all_files_satisfying_the_selector_SHOULD_be_in_model(self):
        # ARRANGE #

        cases = test_data.strip_file_type_info_s(
            test_data.filter_on_file_type(
                FileType.REGULAR,
                [
                    test_data.expected_is_direct_contents_of_actual(case.name, case.value)
                    for case in test_data.cases()
                ]
            )
        )

        def make_model(path: DescribedPath) -> FilesMatcherModel:
            return (
                sut.non_recursive(path)
                    .sub_set(IsRegularFileMatcher())
            )

        # ACT & ASSERT #

        check(self,
              make_model,
              cases)

    def test_WHEN_multiple_selectors_THEN_selection_SHOULD_be_conjunction_of_selectors(self):
        # ARRANGE #

        prefix_to_include = 'A'
        file_type_to_include = FileType.DIRECTORY

        name = prefix_to_include + '-matching-base-name'
        file_name = prefix_to_include + '-matching-base-name--file'
        name1 = prefix_to_include + 'dir-in-dir-matching-base-name'
        name2 = prefix_to_include + '-matching-base-name--dir-in-dir'
        name3 = prefix_to_include + '-matching-base-name'
        name4 = prefix_to_include + '-matching-base-name--empty-dir'
        actual_cases = [
            NameAndValue(
                'empty',
                [],
            ),
            NameAndValue(
                'single regular file that matches on base name',
                [File.empty(name)],
            ),
            NameAndValue(
                'single dir that matches on base name',
                [Dir.empty(name3)],
            ),
            NameAndValue(
                'single dir that not matches on base name',
                [Dir.empty('non-matching-base-name')],
            ),
            NameAndValue(
                'directories with contents - one level',
                [
                    File.empty(file_name),
                    Dir.empty(name4),
                    Dir('non-matching-name-non-empty-dir',
                        [
                            File.empty('file-in-dir'),
                            Dir.empty(name1),
                        ]),
                    Dir(prefix_to_include + '-matching-base-name--non-empty-dir',
                        [
                            File.empty('file-in-dir'),
                            Dir.empty(name2),
                        ]),
                ]
            ),
        ]

        cases = test_data.strip_file_type_info_s(
            test_data.filter_on_file_type(
                file_type_to_include,
                test_data.filter_on_base_name_prefix(
                    prefix_to_include,
                    [
                        test_data.expected_is_direct_contents_of_actual(case.name, case.value)
                        for case in actual_cases
                    ]
                )
            )
        )

        def make_model(path: DescribedPath) -> FilesMatcherModel:
            return (
                sut.non_recursive(path)
                    .sub_set(BaseNameStartsWithMatcher(prefix_to_include))
                    .sub_set(IsDirectoryMatcher())
            )

        # ACT & ASSERT #

        check(self,
              make_model,
              cases)


class IsRegularFileMatcher(FileMatcherTestImplBase):
    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return matching_result.of(
            model.path.primitive.is_file()
        )


class IsDirectoryMatcher(FileMatcherTestImplBase):
    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return matching_result.of(
            model.path.primitive.is_dir()
        )


class BaseNameStartsWithMatcher(FileMatcherTestImplBase):
    def __init__(self, base_name_prefix: str):
        self._base_name_prefix = base_name_prefix

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return matching_result.of(
            model.path.primitive.name.startswith(self._base_name_prefix)
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
