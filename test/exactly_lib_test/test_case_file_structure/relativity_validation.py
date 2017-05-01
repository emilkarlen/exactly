import unittest

from exactly_lib.test_case_file_structure import relativity_validation as sut
from exactly_lib.test_case_file_structure.path_relativity import SPECIFIC_ABSOLUTE_RELATIVITY, RelOptionType, \
    specific_relative_relativity


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestIsSatisfiedBy)


class TestIsSatisfiedBy(unittest.TestCase):
    def runTest(self):
        test_case = [
            (SPECIFIC_ABSOLUTE_RELATIVITY,
             sut.PathRelativityVariants(set(), False),
             False,
             'ACTUAL=absolute, ACCEPTED does NOT accept absolute'
             ),
            (SPECIFIC_ABSOLUTE_RELATIVITY,
             sut.PathRelativityVariants({RelOptionType.REL_ACT}, False),
             False,
             'ACTUAL=absolute, ACCEPTED does NOT accept absolute (but relative is)'
             ),
            (SPECIFIC_ABSOLUTE_RELATIVITY,
             sut.PathRelativityVariants(set(), True),
             True,
             'ACTUAL=absolute, ACCEPTED does accept absolute'
             ),
            (specific_relative_relativity(RelOptionType.REL_ACT),
             sut.PathRelativityVariants(set(), False),
             False,
             'ACTUAL=relative, ACCEPTED does accept relative (and not absolute)'
             ),
            (specific_relative_relativity(RelOptionType.REL_ACT),
             sut.PathRelativityVariants(set(), True),
             False,
             'ACTUAL=relative, ACCEPTED does accept relative (but absolute)'
             ),
            (specific_relative_relativity(RelOptionType.REL_ACT),
             sut.PathRelativityVariants({RelOptionType.REL_CWD,
                                         RelOptionType.REL_HOME},
                                        True),
             False,
             'ACTUAL=relative, ACCEPTED actual NOT IN set of accepted (but absolute)'
             ),
            (specific_relative_relativity(RelOptionType.REL_HOME),
             sut.PathRelativityVariants({RelOptionType.REL_CWD,
                                         RelOptionType.REL_HOME},
                                        True),
             True,
             'ACTUAL=relative, ACCEPTED actual IN set of accepted (but absolute)'
             ),
        ]
        for specific, accepted, expected, description in test_case:
            with self.subTest(msg=description):
                actual = sut.is_satisfied_by(specific, accepted)
                if expected:
                    self.assertTrue(actual)
                else:
                    self.assertFalse(actual)
