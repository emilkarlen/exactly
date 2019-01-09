import unittest

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import tr
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources.instruction_arguments import path_and_matcher
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import \
    EmptyAssertionVariant, argument_constructor_for_emptiness_check, \
    FilesMatcherArgumentsSetup, files_matcher_setup_without_references
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, sym_link, empty_dir, Dir


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        unittest.makeSuite(TestCommonFailureConditions),

        unittest.makeSuite(TestSymbolReferences),

        unittest.makeSuite(TestPassingAndFailingScenarios),
        unittest.makeSuite(TestDifferentSourceVariants),
        unittest.makeSuite(TestWithFileSelection),
    ])


class TestWithAssertionVariantForEmpty(tr.TestWithAssertionVariantBase):
    @property
    def assertion_variant(self) -> FilesMatcherArgumentsSetup:
        return files_matcher_setup_without_references(EmptyAssertionVariant())


class TestParseInvalidSyntax(tr.TestParseInvalidSyntaxBase,
                             TestWithAssertionVariantForEmpty):
    pass


class TestCommonFailureConditions(tr.TestCommonFailureConditionsBase,
                                  TestWithAssertionVariantForEmpty):
    pass


class TestSymbolReferences(tr.TestCommonSymbolReferencesBase,
                           TestWithAssertionVariantForEmpty):
    pass


class TestDifferentSourceVariants(tr.TestCaseBaseForParser):
    def test_file_is_directory_that_is_empty(self):
        empty_directory = empty_dir('name-of-empty-dir')

        instruction_argument_constructor = path_and_matcher(
            empty_directory.name,
            argument_constructor_for_emptiness_check()
        )

        contents_of_relativity_option_root = DirContents([empty_directory])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )

    def test_file_is_a_directory_that_is_not_empty(self):
        non_empty_directory = Dir('name-of-non-empty-dir', [empty_file('file-in-dir')])

        instruction_argument_constructor = path_and_matcher(non_empty_directory.name,
                                                            argument_constructor_for_emptiness_check()
                                                            )

        contents_of_relativity_option_root = DirContents([non_empty_directory])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )

    def test_file_is_directory_with_files_but_none_that_matches_name_pattern(self):
        name_of_directory = 'name-of-directory'
        pattern = 'a*'
        existing_file = empty_file('b')
        instruction_argument_constructor = path_and_matcher(
            name_of_directory,
            argument_constructor_for_emptiness_check(name_option_pattern=pattern)
        )

        contents_of_relativity_option_root = DirContents([Dir(name_of_directory,
                                                              [existing_file])])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )


class TestPassingAndFailingScenarios(tr.TestCaseBaseForParser):
    def test_file_is_directory_that_is_empty(self):
        name_of_empty_directory = 'name-of-empty_directory'
        instruction_argument_constructor = path_and_matcher(
            name_of_empty_directory,
            argument_constructor_for_emptiness_check()
        )

        contents_of_relativity_option_root = DirContents([empty_dir(name_of_empty_directory)])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root)

    def test_file_is_a_directory_that_is_not_empty(self):
        name_of_directory = 'name-of-empty_directory'
        instruction_argument_constructor = path_and_matcher(
            name_of_directory,
            argument_constructor_for_emptiness_check()
        )

        contents_of_relativity_option_root = DirContents([Dir(name_of_directory, [
            empty_file('existing-file-in-checked-dir')
        ])])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.FAIL,
            contents_of_relativity_option_root=contents_of_relativity_option_root)

    def test_file_is_a_symbolic_link_to_an_empty_directory(self):
        name_of_empty_directory = 'name-of-empty_directory'
        name_of_symbolic_link = 'link-to-empty_directory'

        instruction_argument_constructor = path_and_matcher(
            name_of_symbolic_link,
            argument_constructor_for_emptiness_check()
        )

        contents_of_relativity_option_root = DirContents([empty_dir(name_of_empty_directory),
                                                          sym_link(name_of_symbolic_link,
                                                                   name_of_empty_directory)])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root)


class TestWithFileSelection(tr.TestCaseBaseForParser):
    def test_file_is_directory_that_contain_files_but_non_matching_given_name_pattern(self):
        name_of_directory = 'name-of-directory'
        pattern = 'a*'
        existing_file = empty_file('b')
        instruction_argument_constructor = path_and_matcher(
            name_of_directory,
            argument_constructor_for_emptiness_check(name_option_pattern=pattern)
        )

        contents_of_relativity_option_root = DirContents([Dir(name_of_directory,
                                                              [existing_file])])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root)

    def test_file_is_directory_that_contain_files_but_non_matching_given_type_pattern(self):
        type_matcher = FileType.DIRECTORY

        existing_file = empty_file('a-regular-file')

        name_of_directory = 'name-of-directory'

        instruction_argument_constructor = path_and_matcher(
            name_of_directory,
            argument_constructor_for_emptiness_check(type_matcher=type_matcher)
        )

        contents_of_relativity_option_root = DirContents([Dir(name_of_directory,
                                                              [existing_file])])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root)

    def test_file_is_directory_that_contain_files_with_names_that_matches_given_name_pattern(self):
        name_of_directory = 'name-of-directory'
        pattern = 'a*'
        existing_file_1 = empty_file('a1')
        existing_file_2 = empty_file('a2')

        instruction_argument_constructor = path_and_matcher(
            name_of_directory,
            argument_constructor_for_emptiness_check(
                name_option_pattern=pattern)
        )

        contents_of_relativity_option_root = DirContents([Dir(name_of_directory,
                                                              [existing_file_1,
                                                               existing_file_2])])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.FAIL,
            contents_of_relativity_option_root=contents_of_relativity_option_root)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
