import unittest

from shellcheck_lib_test.default.program_modes import test_suite
from shellcheck_lib_test.default.test_resources import default_main_program_suite_preprocessing as pre_proc_tests
from shellcheck_lib_test.default.test_resources import default_main_program_wildcard as wildcard
from shellcheck_lib_test.test_resources.main_program import main_program_check_for_test_suite


class TestTestSuite(main_program_check_for_test_suite.TestsForSetupWithoutPreprocessorExternally):
    def test_empty_file(self):
        self._check(test_suite.EmptySuite())

    def test_suite_with_single_empty_case(self):
        self._check(test_suite.SuiteWithSingleEmptyTestCase())

    def test_suite_with_single_test_case_with_only_section_headers(self):
        self._check(test_suite.SuiteWithSingleTestCaseWithOnlySectionHeaders())

    def test_suite_reference_to_non_existing_case_file(self):
        self._check(test_suite.SuiteReferenceToNonExistingCaseFile())

    def test_suite_reference_to_non_existing_suite_file(self):
        self._check(test_suite.SuiteReferenceToNonExistingSuiteFile())

    def test_suite_with_single_case_with_invalid_syntax(self):
        self._check(test_suite.SuiteWithSingleCaseWithInvalidSyntax())

    def test_complex_successful_suite(self):
        self._check(test_suite.ComplexSuccessfulSuite())


class TestTestSuitesWithWildcardFileReferences(
    main_program_check_for_test_suite.TestsForSetupWithoutPreprocessorExternally):
    def test_references_to_case_files_that_matches_no_files(self):
        self._check(wildcard.ReferencesToCaseFilesThatMatchesNoFiles())

    def test_references_to_case_files_that_are_directories(self):
        self._check(wildcard.ReferencesToCaseFilesThatAreDirectories())

    def test_references_to_suite_files_that_matches_no_files(self):
        self._check(wildcard.ReferencesToSuiteFilesThatMatchesNoFiles())

    def test_references_to_case_files_that_matches_files__type_question_mark(self):
        self._check(wildcard.ReferencesToCaseFilesThatMatchesFilesTypeQuestionMark())

    def test_references_to_case_files_in_any_direct_sub_dir(self):
        self._check(wildcard.ReferencesToCaseFilesInAnyDirectSubDir())

    def test_references_to_suite_files_that_are_directories(self):
        self._check(wildcard.ReferencesToSuiteFilesThatAreDirectories())

    def test_references_to_suite_files_that_matches_files__type_character_range(self):
        self._check(wildcard.ReferencesToSuiteFilesThatMatchesFilesTypeCharacterRange())

    def test_references_to_suite_files_that_matches_files__type_negated_character_range(self):
        self._check(wildcard.ReferencesToSuiteFilesThatMatchesFilesTypeNegatedCharacterRange())

    def test_references_to_suite_files_in_any_sub_dir(self):
        self._check(wildcard.ReferencesToSuiteFilesInAnySubDir())


class TestTestSuitePreprocessing(main_program_check_for_test_suite.TestsForSetupWithPreprocessorExternally):
    def test_empty_file(self):
        self._check(pre_proc_tests.PreprocessorIsAppliedWithTestCaseFileAsArgument())


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestTestSuite))
    ret_val.addTest(unittest.makeSuite(TestTestSuitesWithWildcardFileReferences))
    ret_val.addTest(unittest.makeSuite(TestTestSuitePreprocessing))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
