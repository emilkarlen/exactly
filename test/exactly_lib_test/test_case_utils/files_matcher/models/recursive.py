import unittest

from exactly_lib.test_case_utils.file_matcher.impl.base_class import FileMatcherImplBase
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.files_matcher import models as sut
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources import test_data
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources.checker import check
from exactly_lib_test.test_resources.files.file_structure import Dir, empty_file, \
    empty_dir
from exactly_lib_test.type_system.logic.test_resources import matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCase),
    ])


class TestCase(unittest.TestCase):
    def test_WHEN_no_selector_THEN_all_files_SHOULD_be_in_model(self):
        # ARRANGE #

        cases = test_data.strip_file_type_info(
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

        cases = test_data.strip_file_type_info(
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

        actual_cases = [
            NameAndValue(
                'empty',
                [],
            ),
            NameAndValue(
                'single regular file that matches on base name',
                [empty_file(prefix_to_include + '-matching-base-name')],
            ),
            NameAndValue(
                'single dir that matches on base name',
                [empty_dir(prefix_to_include + '-matching-base-name')],
            ),
            NameAndValue(
                'single dir that not matches on base name',
                [empty_dir('non-matching-base-name')],
            ),
            NameAndValue(
                'directories with contents',
                [
                    empty_file(prefix_to_include + '-matching-base-name--file'),
                    empty_dir(prefix_to_include + '-matching-base-name--empty-dir'),
                    Dir('non-matching-name-non-empty-dir-1',
                        [
                            empty_file('file-in-dir-1-1'),
                            Dir('non-matching-base-name-1-2',
                                [
                                    empty_dir(prefix_to_include + '-matching-base-name--dir-1-2-1')
                                ]),
                        ]),
                    Dir(prefix_to_include + '-matching-base-name--non-empty-dir-2',
                        [
                            empty_file(prefix_to_include + '-matching-base-name--file-2-1'),
                            Dir(prefix_to_include + '-matching-base-name--2-2',
                                [
                                    empty_dir('non-matching-base-name--dir-2-3-1')
                                ]),
                        ]),
                ]
            ),
        ]

        cases = test_data.strip_file_type_info(
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


class FileMatcherTestImplBase(FileMatcherImplBase):
    @property
    def name(self) -> str:
        return str(type(self))

    def _structure(self) -> StructureRenderer:
        return renderers.header_only(self.name)


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
