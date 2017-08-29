import unittest

from exactly_lib.test_case_utils.lines_transformers import parse_lines_transformer as sut
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test(self):
        sut.parse_lines_transformer(remaining_source(sut.WITH_REPLACED_ENV_VARS_OPTION))
