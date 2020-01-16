import unittest
from pathlib import Path

from exactly_lib.processing import test_case_processing
from exactly_lib.processing.test_case_processing import new_executed, \
    TestCaseFileReference, Result
from exactly_lib.test_suite import processing as sut
from exactly_lib.test_suite.enumeration import DepthFirstEnumerator
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.processing.test_resources.test_case_processing_assertions import equals_test_case_reference
from exactly_lib_test.test_resources.files.str_std_out_files import null_output_reporting_environment
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_suite.processing.basic_scenarios import ReaderThatGivesConstantSuite
from exactly_lib_test.test_suite.test_resources.processing_utils import \
    FULL_RESULT_PASS, test_suite, DUMMY_CASE_PROCESSING
from exactly_lib_test.test_suite.test_resources.suite_reporting import ProcessingReporterThatDoesNothing


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([Test()])


class Test(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        path_cases = [
            NameAndValue('relative file name',
                         TestCaseFileReference(Path('test.case'),
                                               Path('reference') / 'relativity')
                         ),
            NameAndValue('absolute file name',
                         TestCaseFileReference(Path.cwd() / 'test.case',
                                               Path.cwd())),
        ]

        for path_case in path_cases:
            test_case_paths_expectation = asrt.matches_sequence([
                equals_test_case_reference(path_case.value)
            ])

            suite_with_case = test_suite(
                source_file_name='ignored',
                sub_test_suites=[],
                test_cases=[path_case.value],
            )
            suite_cases = [
                NameAndValue('case in root suite',
                             suite_with_case,
                             ),
                NameAndValue('case in sub suite',
                             test_suite(
                                 source_file_name='ignored',
                                 sub_test_suites=[suite_with_case],
                                 test_cases=[]
                             ),
                             ),
            ]
            for suite_case in suite_cases:
                with self.subTest(path_case=path_case.name,
                                  suite_case=suite_case.name):
                    suite_hierarchy_reader = ReaderThatGivesConstantSuite(suite_case.value)
                    reporter = ProcessingReporterThatDoesNothing()
                    path_registering_processor = TestCaseProcessorThatJustRegistersTestCaseFileReference()
                    processor = sut.Processor(DUMMY_CASE_PROCESSING,
                                              suite_hierarchy_reader,
                                              reporter,
                                              DepthFirstEnumerator(),
                                              lambda config: path_registering_processor)
                    # ACT #
                    return_value = processor.process(suite_case.value.source_file, null_output_reporting_environment())
                    # ASSERT #
                    self.assertEqual(ProcessingReporterThatDoesNothing.VALID_SUITE_EXIT_CODE,
                                     return_value,
                                     'Sanity check of result indicator')

                    test_case_paths_expectation.apply_without_message(
                        self,
                        path_registering_processor.recording_media
                    )


class TestCaseProcessorThatJustRegistersTestCaseFileReference(test_case_processing.Processor):
    def __init__(self):
        self.recording_media = []

    def apply(self, test_case: TestCaseFileReference) -> Result:
        self.recording_media.append(test_case)
        return new_executed(FULL_RESULT_PASS)
