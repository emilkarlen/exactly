from typing import List

from exactly_lib.test_suite.structure import TestSuiteHierarchy


class SuiteEnumerator:
    """
    Determines in what order the suites should be executed.
    """

    def apply(self, suite: TestSuiteHierarchy) -> List[TestSuiteHierarchy]:
        """
        Enumerates all suites contained in the argument.
        :param suite: Root of suites to be enumerated.
        :return: All suites in the given suite hierarchy.
        """
        raise NotImplementedError()


class DepthFirstEnumerator(SuiteEnumerator):
    def apply(self, suite: TestSuiteHierarchy) -> List[TestSuiteHierarchy]:
        ret_val = []
        for sub_suite in suite.sub_test_suites:
            ret_val += self.apply(sub_suite)
        ret_val.append(suite)
        return ret_val
