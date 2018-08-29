from exactly_lib.processing.test_case_handling_setup import TestCaseTransformer
from exactly_lib.section_document.model import SectionContents
from exactly_lib.test_case.test_case_doc import TestCase
from exactly_lib.test_suite import test_suite_doc


class TestCaseInstructionsFromTestSuiteAdder(TestCaseTransformer):
    def __init__(self, test_suite: test_suite_doc.TestSuiteDocument):
        self._test_suite = test_suite

    def transform(self, test_case: TestCase) -> TestCase:
        return TestCase(
            configuration_phase=test_case.configuration_phase,
            setup_phase=self._append(self._test_suite.case_setup, test_case.setup_phase),
            act_phase=test_case.act_phase,
            before_assert_phase=self._append(self._test_suite.case_before_assert, test_case.before_assert_phase),
            assert_phase=self._append(self._test_suite.case_assert, test_case.assert_phase),
            cleanup_phase=self._append(test_case.cleanup_phase, self._test_suite.case_cleanup),
        )

    @staticmethod
    def _append(fst: SectionContents, snd: SectionContents) -> SectionContents:
        return SectionContents(tuple(list(fst.elements) + list(snd.elements)))
