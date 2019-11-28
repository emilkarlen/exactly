import unittest

from exactly_lib.test_case_utils.matcher.impls import constant as sut
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestConstant)


class TestConstant(unittest.TestCase):
    def runTest(self):
        cases = [
            NEA('constant true should match',
                True,
                True,
                ),
            NEA('constant false should not match',
                False,
                False,
                ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                matcher = sut.MatcherWithConstantResult(case.actual)
                # ACT #
                actual_result = matcher.matches_w_trace(None)

                # ASSERT #

                asrt_matching_result.matches_value(case.expected).apply_with_message(self,
                                                                                     actual_result,
                                                                                     'matching result')
