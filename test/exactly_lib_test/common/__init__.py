import unittest

from exactly_lib_test.common.help import see_also


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(see_also.SeeAlsoItemVisitorTest)
