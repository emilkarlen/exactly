import unittest

from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic import matcher_base_class as sut
from exactly_lib.type_system.logic.matcher_base_class import MODEL
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.std_type_visitor import MatcherStdTypeVisitorTestAcceptImpl, \
    assert_argument_satisfies__and_return


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMatcherBaseClass),
    ])


class TestMatcherBaseClass(unittest.TestCase):
    def test_accept_SHOULD_invoke_method_for_non_standard_matcher(self):
        matcher = _BaseClassTestImpl()
        return_value = 5
        visitor = MatcherStdTypeVisitorTestAcceptImpl.new_w_default_to_raise_exception(
            non_standard_action=assert_argument_satisfies__and_return(self, asrt.is_(matcher), return_value)
        )
        # ACT & ASSERT #
        actual_return_value = matcher.accept(visitor)
        # ASSERT #
        self.assertEqual(return_value, actual_return_value, 'return value')


class _BaseClassTestImpl(sut.MatcherWTrace):
    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        raise ValueError('should not be used')

    @property
    def name(self) -> str:
        raise ValueError('should not be used')

    def structure(self) -> StructureRenderer:
        raise ValueError('should not be used')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
