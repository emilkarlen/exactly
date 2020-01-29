import unittest

from exactly_lib.test_case_utils.expression import syntax_documentation as sut
from exactly_lib_test.common.help.test_resources.see_also_assertions import is_see_also_target_list
from exactly_lib_test.common.help.test_resources.syntax_contents_structure_assertions import \
    is_syntax_element_description
from exactly_lib_test.test_case_utils.expression import test_resources
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_syntax_element_description(self):
        actual = sut.syntax_element_description(test_resources.GRAMMAR_WITH_ALL_COMPONENTS)
        is_syntax_element_description.apply_without_message(self, actual)

    def test_syntax_element_descriptions(self):
        syntax = sut.Syntax(test_resources.GRAMMAR_WITH_ALL_COMPONENTS)
        actual = syntax.syntax_element_descriptions()
        self.assertGreater(len(actual), 0, 'number of syntax element descriptions')
        asrt.is_sequence_of(is_syntax_element_description).apply_without_message(self, actual)

    def test_see_also_set(self):
        syntax = sut.Syntax(test_resources.GRAMMAR_WITH_ALL_COMPONENTS)
        actual = syntax.see_also_targets()
        is_see_also_target_list.apply_without_message(self, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
