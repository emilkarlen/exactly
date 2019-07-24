import unittest

from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb
from exactly_lib.util.simple_textstruct.structure import MinorBlock, MajorBlock, LineElement, StringLineObject
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
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
            NameAndValue('empty list of blocks',
                         rend_comb.ConstantR([]),
                         ),
            NameAndValue('non-empty list of blocks',
                         rend_comb.ConstantR([MajorBlock([])]),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                sut.is_renderer_of_major_blocks().apply_without_message(self, case.value)

    def test_not_matches(self):
        cases = [
            NameAndValue('not a renderer',
                         MajorBlock([]),
                         ),
            NameAndValue('not a sequence',
                         rend_comb.ConstantR(MajorBlock([])),
                         ),
            NameAndValue('not a major block',
                         rend_comb.ConstantR([MinorBlock([])]),
                         ),
            NameAndValue('invalid contents of block',
                         rend_comb.ConstantR([MajorBlock(['not a minor block'])]),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(sut.is_renderer_of_major_blocks(), case.value)


class TestIsRendererOfMinorBlocks(unittest.TestCase):
    def test_matches(self):
        cases = [
            NameAndValue('empty list of blocks',
                         rend_comb.ConstantR([]),
                         ),
            NameAndValue('non-empty list of blocks',
                         rend_comb.ConstantR([MinorBlock([])]),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                sut.is_renderer_of_minor_blocks().apply_without_message(self, case.value)

    def test_not_matches(self):
        cases = [
            NameAndValue('not a renderer',
                         MajorBlock([]),
                         ),
            NameAndValue('not a sequence',
                         rend_comb.ConstantR(MajorBlock([])),
                         ),
            NameAndValue('not a minor block',
                         rend_comb.ConstantR([MajorBlock([])]),
                         ),
            NameAndValue('invalid contents of block',
                         rend_comb.ConstantR([MinorBlock(['not a minor block'])]),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(sut.is_renderer_of_minor_blocks(), case.value)


class TestIsRendererOfLineElements(unittest.TestCase):
    _LINE_ELEMENT = LineElement(StringLineObject('string'))

    def test_matches(self):
        cases = [
            NameAndValue('empty list of blocks',
                         rend_comb.ConstantR([]),
                         ),
            NameAndValue('non-empty list of line elements',
                         rend_comb.ConstantR([self._LINE_ELEMENT]),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                sut.is_renderer_of_line_elements().apply_without_message(self, case.value)

    def test_not_matches(self):
        cases = [
            NameAndValue('not a renderer',
                         self._LINE_ELEMENT,
                         ),
            NameAndValue('not a sequence',
                         rend_comb.ConstantR(self._LINE_ELEMENT),
                         ),
            NameAndValue('not a line element',
                         rend_comb.ConstantR([MajorBlock([])]),
                         ),
            NameAndValue('invalid contents of line element',
                         rend_comb.ConstantR([LineElement(StringLineObject('string'), 'not properties')]),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(sut.is_renderer_of_line_elements(), case.value)
