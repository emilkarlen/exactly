import unittest

from exactly_lib.test_case_utils.expression import syntax_documentation as sut
from exactly_lib_test.common.help.test_resources.syntax_contents_structure_assertions import \
    is_syntax_element_description
from exactly_lib_test.test_case_utils.expression import test_resources


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_syntax_element_description(self):
        actual = sut.syntax_element_description(test_resources.GRAMMAR_WITH_ALL_COMPONENTS)
        is_syntax_element_description.apply_without_message(self, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
