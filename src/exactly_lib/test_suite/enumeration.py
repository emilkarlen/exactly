from exactly_lib.test_suite.structure import TestSuite


class SuiteEnumerator:
    """
    Determines in what order the suites should be executed.
    """

    def apply(self,
              suite: TestSuite) -> list:
        """
        Enumerates all suites contained in the argument.
        :param suite: Root of suites to be enumerated.
        :return: [TestSuite] All suites in the given suite hierarchy.
        """
        raise NotImplementedError()


class DepthFirstEnumerator(SuiteEnumerator):
    def apply(self, suite: TestSuite) -> list:
        ret_val = []
        for sub_suite in suite.sub_test_suites:
            ret_val.extend(self.apply(sub_suite))
        ret_val.append(suite)
        return ret_val
