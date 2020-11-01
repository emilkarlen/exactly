import unittest
from typing import List, Callable

from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.files_matcher import models as sut
from exactly_lib.type_val_deps.types.path.path_ddv import DescribedPath
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_case_utils.file_matcher.test_resources.file_matchers import IsRegularFileMatcher, \
    IsDirectoryMatcher, BaseNameStartsWithMatcher
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources import test_data
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources.checker import check, check_single
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources.test_data import FileElementForTest
from exactly_lib_test.test_resources.files.file_structure import Dir, FileSystemElement, File
from exactly_lib_test.test_resources.test_utils import EA


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestUnlimitedDepth),
        unittest.makeSuite(TestMaxDepth),
        unittest.makeSuite(TestMinDepth),
        unittest.makeSuite(TestMinAndMaxDepth),
    ])


class TestMaxDepth(unittest.TestCase):
    def runTest(self):
        for max_depth in range(4):

            def make_model(path: DescribedPath) -> FilesMatcherModel:
                return sut.recursive(path,
                                     max_depth=max_depth)

            for model_case in test_data.DEPTH_TEST_MODELS:
                with self.subTest(model=model_case.name,
                                  max_depth=max_depth):
                    case = test_data.expected_is_actual_down_to_max_depth(
                        max_depth,
                        model_case.value,
                    )

                    _check_single(self, make_model, case)


class TestMinDepth(unittest.TestCase):
    def runTest(self):
        for min_depth in range(4):

            def make_model(path: DescribedPath) -> FilesMatcherModel:
                return sut.recursive(path,
                                     min_depth=min_depth)

            for model_case in test_data.DEPTH_TEST_MODELS:
                with self.subTest(model=model_case.name,
                                  min_depth=min_depth):
                    case = test_data.expected_is_actual_from_min_depth(
                        min_depth,
                        model_case.value,
                    )

                    _check_single(self, make_model, case)


class TestMinAndMaxDepth(unittest.TestCase):
    def runTest(self):
        for min_depth in range(4):
            for max_depth in range(4):

                def make_model(path: DescribedPath) -> FilesMatcherModel:
                    return sut.recursive(path,
                                         min_depth=min_depth,
                                         max_depth=max_depth)

                for model_case in test_data.DEPTH_TEST_MODELS:
                    with self.subTest(model=model_case.name,
                                      min_depth=min_depth,
                                      max_depth=max_depth):
                        case = test_data.expected_is_actual_within_depth_limits(
                            min_depth,
                            max_depth,
                            model_case.value,
                        )

                    _check_single(self, make_model, case)


class TestUnlimitedDepth(unittest.TestCase):
    def test_WHEN_no_selector_THEN_all_files_SHOULD_be_in_model(self):
        # ARRANGE #

        cases = test_data.strip_file_type_info_s(
            [
                test_data.identical_expected_and_actual(case.name, case.value)
                for case in test_data.cases()
            ]
        )

        # ACT & ASSERT #

        check(self,
              sut.recursive,
              cases)

    def test_WHEN_single_selector_THEN_all_files_satisfying_the_selector_SHOULD_be_in_model(self):
        # ARRANGE #

        cases = test_data.strip_file_type_info_s(
            test_data.filter_on_file_type(
                FileType.REGULAR,
                [
                    test_data.identical_expected_and_actual(case.name, case.value)
                    for case in test_data.cases()
                ]
            )
        )

        def make_model(path: DescribedPath) -> FilesMatcherModel:
            return (
                sut.recursive(path)
                    .sub_set(IsRegularFileMatcher())
            )

        # ACT & ASSERT #

        check(self,
              make_model,
              cases)

    def test_WHEN_multiple_selectors_THEN_selection_SHOULD_be_conjunction_of_selectors(self):
        # ARRANGE #

        prefix_to_include = 'INCLUDE'
        file_type_to_include = FileType.DIRECTORY

        name = prefix_to_include + '-matching-base-name--file-2-1'
        file_name = prefix_to_include + '-matching-base-name'
        name1 = prefix_to_include + '-matching-base-name--file'
        name2 = prefix_to_include + '-matching-base-name--dir-1-2-1'
        name3 = prefix_to_include + '-matching-base-name'
        name4 = prefix_to_include + '-matching-base-name--empty-dir'
        actual_cases = [
            NameAndValue(
                'empty',
                [],
            ),
            NameAndValue(
                'single regular file that matches on base name',
                [File.empty(file_name)],
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
                'directories with contents',
                [
                    File.empty(name1),
                    Dir.empty(name4),
                    Dir('non-matching-name-non-empty-dir-1',
                        [
                            File.empty('file-in-dir-1-1'),
                            Dir('non-matching-base-name-1-2',
                                [
                                    Dir.empty(name2)
                                ]),
                        ]),
                    Dir(prefix_to_include + '-matching-base-name--non-empty-dir-2',
                        [
                            File.empty(name),
                            Dir(prefix_to_include + '-matching-base-name--2-2',
                                [
                                    Dir.empty('non-matching-base-name--dir-2-3-1')
                                ]),
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
                        test_data.identical_expected_and_actual(case.name, case.value)
                        for case in actual_cases
                    ]
                )
            )
        )

        def make_model(path: DescribedPath) -> FilesMatcherModel:
            return (
                sut.recursive(path)
                    .sub_set(BaseNameStartsWithMatcher(prefix_to_include))
                    .sub_set(IsDirectoryMatcher())
            )

        # ACT & ASSERT #

        check(self,
              make_model,
              cases)


def _check_single(put: unittest.TestCase,
                  make_model: Callable[[DescribedPath], FilesMatcherModel],
                  case: EA[List[FileElementForTest], List[FileSystemElement]],
                  ):
    prepared_case = test_data.strip_file_type_info__ea(case)
    check_single(put,
                 make_model,
                 prepared_case.actual,
                 prepared_case.expected)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
