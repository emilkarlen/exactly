import unittest

from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb
from exactly_lib.util.simple_textstruct.structure import MinorBlock, MajorBlock, LineElement, StringLineObject
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsRendererOfMajorBlocks),
        unittest.makeSuite(TestIsRendererOfMinorBlocks),
        unittest.makeSuite(TestIsRendererOfLineElements),
    ])


class TestIsRendererOfMajorBlocks(unittest.TestCase):
    def test_matches(self):
        cases = [
            NIE('default assertion/empty list of blocks',
                input_value=rend_comb.ConstantR([]),
                expected_value=sut.is_renderer_of_major_blocks(),
                ),
            NIE('default assertion/non-empty list of blocks',
                input_value=rend_comb.ConstantR([MajorBlock([])]),
                expected_value=sut.is_renderer_of_major_blocks(),
                ),
            NIE('custom assertion',
                input_value=rend_comb.ConstantR([MajorBlock([])]),
                expected_value=sut.is_renderer_of_major_blocks(asrt.len_equals(1)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected_value.apply_without_message(self, case.input_value)

    def test_not_matches(self):
        cases = [
            NIE('default assertion/not a renderer',
                input_value=MajorBlock([]),
                expected_value=sut.is_renderer_of_major_blocks(),
                ),
            NIE('default assertion/not a sequence',
                input_value=rend_comb.ConstantR(MajorBlock([])),
                expected_value=sut.is_renderer_of_major_blocks(),
                ),
            NIE('default assertion/not a major block',
                input_value=rend_comb.ConstantR([MinorBlock([])]),
                expected_value=sut.is_renderer_of_major_blocks(),
                ),
            NIE('default assertion/invalid contents of block',
                input_value=rend_comb.ConstantR([MajorBlock(['not a minor block'])]),
                expected_value=sut.is_renderer_of_major_blocks(),
                ),
            NIE('custom assertion/unexpected number of blocks',
                input_value=rend_comb.ConstantR([]),
                expected_value=sut.is_renderer_of_major_blocks(asrt.len_equals(1)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected_value, case.input_value)


class TestIsRendererOfMinorBlocks(unittest.TestCase):
    def test_matches(self):
        cases = [
            NIE('default assertion/empty list of blocks',
                input_value=rend_comb.ConstantR([]),
                expected_value=sut.is_renderer_of_minor_blocks(),
                ),
            NIE('default assertion/non-empty list of blocks',
                input_value=rend_comb.ConstantR([MinorBlock([])]),
                expected_value=sut.is_renderer_of_minor_blocks(),
                ),
            NIE('custom assertion',
                input_value=rend_comb.ConstantR([MinorBlock([])]),
                expected_value=sut.is_renderer_of_minor_blocks(asrt.len_equals(1)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected_value.apply_without_message(self, case.input_value)

    def test_not_matches(self):
        cases = [
            NIE('default assertion/not a renderer',
                input_value=MajorBlock([]),
                expected_value=sut.is_renderer_of_minor_blocks(),
                ),
            NIE('default assertion/not a sequence',
                input_value=rend_comb.ConstantR(MajorBlock([])),
                expected_value=sut.is_renderer_of_minor_blocks(),
                ),
            NIE('default assertion/not a minor block',
                input_value=rend_comb.ConstantR([MajorBlock([])]),
                expected_value=sut.is_renderer_of_minor_blocks(),
                ),
            NIE('default assertion/invalid contents of block',
                input_value=rend_comb.ConstantR([MinorBlock(['not a minor block'])]),
                expected_value=sut.is_renderer_of_minor_blocks(),
                ),
            NIE('custom assertion/unexpected number of blocks',
                input_value=rend_comb.ConstantR([]),
                expected_value=sut.is_renderer_of_minor_blocks(asrt.len_equals(1)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected_value, case.input_value)


class TestIsRendererOfLineElements(unittest.TestCase):
    _LINE_ELEMENT = LineElement(StringLineObject('string'))

    def test_matches(self):
        cases = [
            NIE('default assertion/empty list of blocks',
                input_value=rend_comb.ConstantR([]),
                expected_value=sut.is_renderer_of_line_elements(),
                ),
            NIE('default assertion/non-empty list of line elements',
                input_value=rend_comb.ConstantR([self._LINE_ELEMENT]),
                expected_value=sut.is_renderer_of_line_elements(),
                ),
            NIE('custom assertion',
                input_value=rend_comb.ConstantR([self._LINE_ELEMENT]),
                expected_value=sut.is_renderer_of_line_elements(asrt.len_equals(1)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected_value.apply_without_message(self, case.input_value)

    def test_not_matches(self):
        cases = [
            NIE('default assertion/not a renderer',
                input_value=self._LINE_ELEMENT,
                expected_value=sut.is_renderer_of_line_elements(),
                ),
            NIE('default assertion/not a sequence',
                input_value=rend_comb.ConstantR(self._LINE_ELEMENT),
                expected_value=sut.is_renderer_of_line_elements(),
                ),
            NIE('default assertion/not a line element',
                input_value=rend_comb.ConstantR([MajorBlock([])]),
                expected_value=sut.is_renderer_of_line_elements(),
                ),
            NIE('default assertion/invalid contents of line element',
                input_value=rend_comb.ConstantR([LineElement(StringLineObject('string'), 'not properties')]),
                expected_value=sut.is_renderer_of_line_elements(),
                ),
            NIE('custom assertion/unexpected number of blocks',
                input_value=rend_comb.ConstantR([]),
                expected_value=sut.is_renderer_of_line_elements(asrt.len_equals(1)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected_value, case.input_value)
